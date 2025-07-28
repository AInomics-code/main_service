from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_openai_tools_agent
from .prompt import INVENTORY_AGENT_PROMPT
from config.settings import settings
from ..registry import BaseAgent, register_agent
from tools.sqlserver_database_tool import SQLServerDatabaseTool
from typing import Dict, Any

@register_agent("InventoryAgent")
class InventoryAgent(BaseAgent):
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
        self.prompt = ChatPromptTemplate.from_template(INVENTORY_AGENT_PROMPT)
        
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
    
    def run(self, user_input: str, database_schema: Dict[str, Any] = None, relevant_schema_content: str = None) -> str:
        """Método estándar que implementa la interfaz BaseAgent"""
        try:
            # Usar schema externo si se proporciona, sino usar el interno
            schema_to_use = database_schema if database_schema else self.database_schema
            
            # Use our custom agent with the database schema
            response = self.agent_executor.invoke({
                "user_input": user_input,
                "database_schema": str(schema_to_use),
                "relevant_schema_content": relevant_schema_content or "No relevant schema content provided"
            })
            return response.get("output", "No se pudo obtener respuesta de la base de datos.")
        except Exception as e:
            return f"Error al procesar la consulta de inventario: {str(e)}"
    
    def analyze_inventory(self, user_input: str) -> str:
        """Método específico para análisis de inventario"""
        return self.run(user_input) 