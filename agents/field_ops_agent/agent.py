from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_openai_tools_agent
from .prompt import FIELD_OPS_AGENT_PROMPT
from config.settings import settings
from ..registry import BaseAgent, register_agent
from tools.sqlserver_database_tool import SQLServerDatabaseTool

@register_agent("FieldOpsAgent")
class FieldOpsAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=settings.OPENAI_KEY
        )
        
        # Initialize SQL Server database tool
        self.db_tool = SQLServerDatabaseTool(llm=self.llm)
        
        # Get database schema from cache
        self.database_schema = self.db_tool.get_cached_schema_json()
        
        # Create prompt template with database schema
        self.prompt = ChatPromptTemplate.from_template(FIELD_OPS_AGENT_PROMPT)
        
        # Create custom agent with database tools and our prompt
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.db_tool.get_tools(),
            prompt=self.prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.db_tool.get_tools(),
            verbose=True
        )
    
    def run(self, user_input: str) -> str:
        """Método estándar que implementa la interfaz BaseAgent"""
        try:
            # Use our custom agent with the database schema
            response = self.agent_executor.invoke({
                "user_input": user_input,
                "database_schema": str(self.database_schema)
            })
            return response.get("output", "No se pudo obtener respuesta de la base de datos.")
        except Exception as e:
            return f"Error al procesar la consulta de operaciones de campo: {str(e)}"
    
    def analyze_field_ops(self, user_input: str) -> str:
        """Método específico para análisis de operaciones de campo"""
        return self.run(user_input) 