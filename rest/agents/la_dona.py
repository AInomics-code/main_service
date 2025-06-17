# rest/agents/la_dona.py
import logging
import uuid
import redis

from fastapi import Request
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.memory import RedisChatMessageHistory, ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder

from ..tools.database_tool import DatabaseTool
from config.settings import settings

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# 1. MODELO LLM
# ──────────────────────────────────────────────────────────────────────────────
# Modelo más rápido pero con limitaciones en herramientas
# llm = ChatOpenAI(
#     model="gpt-3.5-turbo",
#     temperature=0,
#     openai_api_key=settings.OPENAI_KEY
# )

# Modelo más preciso y con mejor soporte para herramientas
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    openai_api_key=settings.OPENAI_KEY,
    request_timeout=30,  # Timeout más corto para respuestas más rápidas
    max_retries=2,      # Menos reintentos para fallar más rápido si hay problemas
    streaming=False     # Desactivar streaming para respuestas más directas
)

# ──────────────────────────────────────────────────────────────────────────────
# 2. TOOLS
# ──────────────────────────────────────────────────────────────────────────────
db_tool = DatabaseTool(llm=llm)
schema_json = db_tool.get_cached_schema_json()

# ──────────────────────────────────────────────────────────────────────────────
# 3. PROMPT DEL AGENTE
# ──────────────────────────────────────────────────────────────────────────────

def build_schema_context(schema_data):
    """Build a readable database schema context for the agent"""
    context = "\nDATABASE SCHEMA INFORMATION:\n"
    context += f"Database: {schema_data.get('database_name', 'Unknown')}\n"
    context += f"Total Tables: {schema_data.get('table_count', 0)}\n\n"
    
    for table in schema_data.get('tables', []):
        context += f"TABLE: {table['table_name']}\n"
        context += "Columns:\n"
        
        for column in table['columns']:
            nullable = "NULL" if column.get('is_nullable', True) else "NOT NULL"
            
            context += f"  - {column['column_name']}: {column['data_type']} {nullable}\n"
        
        context += "\n"
    
    return context

schema_context = build_schema_context(schema_json)

SYSTEM_MESSAGE = f"""You are a professional retail analyst with expertise in sales performance, customer insights, and product analytics.
Your role is to serve sales departments and management teams by providing data-driven insights and actionable recommendations.

{schema_context}

IMPORTANT GUIDELINES:

1. DATABASE KNOWLEDGE: You have complete knowledge of the database schema above. Use this information to:
   - Generate accurate SQL queries without needing to explore the database structure
   - Understand table relationships and foreign keys
   - Write efficient queries that leverage the known schema
   - Avoid unnecessary database exploration queries

2. LANGUAGE DETECTION AND RESPONSE: 
   - CRITICAL: You MUST detect the language of the user's input query and respond in that EXACT SAME LANGUAGE
   - Analyze the specific words and phrases in the user's query to determine the language
   - If the query contains Spanish words (como, cómo, qué, cuánto, ventas, clientes, productos, etc.), respond completely in Spanish
   - If the query contains English words (what, how, sales, customers, products, etc.), respond completely in English
   - If the query contains French words, respond in French
   - The language of your response must match the language detected in the user's input query
   - Do NOT mix languages in your response - use only the detected language

3. CONTEXT AWARENESS: You have access to the chat history. When a question refers to previous information (using words like 'ese', 'ese mes', 'antes', etc.), 
you MUST check the chat history to understand the context. The chat history is available to you in the 'chat_history' variable.

4. CURRENCY FORMATTING: When presenting monetary amounts, format them as currency using the appropriate format for the user's language:
   - For Spanish: Use dot (.) for thousands separator and comma (,) for decimals (e.g., $1.234.567,89)
   - For English: Use comma (,) for thousands separator and dot (.) for decimals (e.g., $1,234,567.89)
   - Always include the currency symbol ($) and format numbers with appropriate decimal places

5. USER-FRIENDLY RESPONSES: 
   - NEVER include database field names, column names, or internal IDs in your responses
   - Present information in natural, business-friendly language
   - Focus on insights and actionable information rather than raw data
   - Use clear, descriptive terms instead of technical database terminology
   - When referring to customers, use names or descriptive terms, not IDs
   - When referring to products, use product names or categories, not internal codes

6. EFFICIENCY: Since you know the complete database schema, write SQL queries directly without exploring the database structure first. This will provide faster responses to users.

7. QUERY OPTIMIZATION: To minimize database calls and improve response time:
   - ALWAYS try to answer questions with a SINGLE SQL query whenever possible
   - Use Common Table Expressions (CTEs) when you need multiple steps or complex calculations
   - Prefer JOINs over multiple separate queries to get related data
   - Use subqueries and window functions to aggregate and calculate data in one query
   - When analyzing trends or comparisons, use CTEs to organize your logic but execute everything in one statement
   - Examples of efficient patterns:
     * Use CTEs to first filter data, then aggregate: WITH filtered_data AS (...) SELECT ... FROM filtered_data
     * Use window functions for rankings, running totals, or period comparisons
     * Use CASE statements for conditional aggregations instead of multiple queries
   - Only use multiple queries if the analysis truly requires it (e.g., completely unrelated datasets)
   - Remember: ONE comprehensive query is always better than multiple simple queries"""

# ──────────────────────────────────────────────────────────────────────────────
# 4. FUNCIÓN PRINCIPAL
# ──────────────────────────────────────────────────────────────────────────────
async def process(request: Request):
    """
    Endpoint handler que recibe:
    {
        "query": "pregunta del usuario",
        "context_id": "uuid-opcional"
    }
    Devuelve:
    {
        "response": "respuesta del agente",
        "context_id": "uuid"
    }
    """
    try:
        body = await request.json()
        logger.debug("Request body: %s", body)

        query: str | None = body.get("query")
        context_id: str | None = body.get("context_id")

        if not query:
            return {"error": "No query provided in request body"}

        if not context_id:
            context_id = str(uuid.uuid4())

        try:
            redis_client = redis.Redis(host="localhost", port=6379, db=0)
            redis_client.ping()
        except redis.ConnectionError as exc:
            logger.error("Redis connection error: %s", exc)
            return {"error": "Redis unavailable"}

        message_history = RedisChatMessageHistory(
            url="redis://localhost:6379",
            session_id=context_id,
            ttl=86_400
        )

        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            chat_memory=message_history
        )

        agent = initialize_agent(
            tools=db_tool.get_tools(),
            llm=llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True,
            agent_kwargs={
                "system_message": SYSTEM_MESSAGE,
                "extra_prompt_messages": [MessagesPlaceholder(variable_name="chat_history")]
            }
        )

        response = agent.run(input=query)

        return {
            "response": response,
            "context_id": context_id
        }

    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        return {"error": str(exc)}
