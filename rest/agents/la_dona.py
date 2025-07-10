# rest/agents/la_dona.py
import logging
import uuid
import redis

from fastapi import Request
from langchain.agents import initialize_agent, AgentType
from langchain_community.chat_models import ChatOpenAI
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import MessagesPlaceholder

from ..tools.sqlserver_database_tool import SQLServerDatabaseTool
from ..prompts.la_dona_prompt import get_system_message, build_schema_context
from config.settings import settings

from langdetect import detect, LangDetectException

logger = logging.getLogger(__name__)

def detect_lang(text: str) -> str:
    try:
        return detect(text)
    except LangDetectException:
        return "en"

# ──────────────────────────────────────────────────────────────────────────────
# 1. MODELO LLM
# ──────────────────────────────────────────────────────────────────────────────
llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0,
    openai_api_key=settings.OPENAI_KEY,
    request_timeout=30,  # Timeout más corto para respuestas más rápidas
    max_retries=2,      # Menos reintentos para fallar más rápido si hay problemas
    streaming=False     # Desactivar streaming para respuestas más directas
)

# ──────────────────────────────────────────────────────────────────────────────
# 2. TOOLS
# ──────────────────────────────────────────────────────────────────────────────
db_tool = SQLServerDatabaseTool(llm=llm)

# ──────────────────────────────────────────────────────────────────────────────
# 3. PROMPT DEL AGENTE
# ──────────────────────────────────────────────────────────────────────────────
schema_json = db_tool.get_cached_schema_json()
schema_context = build_schema_context(schema_json)
SYSTEM_MESSAGE = get_system_message(schema_context)

# ──────────────────────────────────────────────────────────────────────────────
# 4. FUNCIÓN PRINCIPAL
# ──────────────────────────────────────────────────────────────────────────────
async def process(request: Request):
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

        # Usar memoria con ventana para limitar el contexto
        memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            chat_memory=message_history,
            k=10  # Mantener solo los últimos 10 mensajes
        )

        # Get all available tools (database + custom business tools)
        all_tools = db_tool.get_tools()

        # Mantener el agente conversacional pero con mejor configuración
        agent = initialize_agent(
            tools=all_tools,
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
