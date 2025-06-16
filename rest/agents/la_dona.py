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

# ──────────────────────────────────────────────────────────────────────────────
# 3. PROMPT DEL AGENTE
# ──────────────────────────────────────────────────────────────────────────────
SYSTEM_MESSAGE = """You are a professional retail analyst with expertise in sales performance, customer insights, and product analytics.
Your role is to serve sales departments and management teams by providing data-driven insights and actionable recommendations.

IMPORTANT: You have access to the chat history. When a question refers to previous information (using words like 'ese', 'ese mes', 'antes', etc.), 
you MUST check the chat history to understand the context. The chat history is available to you in the 'chat_history' variable.

Always respond in the same language as the query."""

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
