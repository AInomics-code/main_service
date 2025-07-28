from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_openai_tools_agent
from .prompt import SUPERVISOR_PROMPT
from config.settings import settings
from ..registry import BaseAgent, register_agent
from tools.sqlserver_database_tool import SQLServerDatabaseTool
from typing import Dict, Any

@register_agent("Supervisor")
class SupervisorAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            openai_api_key=settings.OPENAI_KEY
        )
        
        # Initialize SQL Server database tool
        self.db_tool = SQLServerDatabaseTool(llm=self.llm)
        
        # Get database schema from cache
        self.database_schema = self.db_tool.get_cached_schema_json()
        
        # Create prompt template with database schema
        self.prompt = ChatPromptTemplate.from_template(SUPERVISOR_PROMPT)
        
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
            return f"Error al procesar la consulta: {str(e)}"
    
    def combine_results(self, user_input: str, pipeline_plan: str, detected_language: str, agent_results: str, relevant_schema_content: str = None) -> str:
        """Método específico para combinar resultados"""
        try:
            response = self.agent_executor.invoke({
                "user_input": user_input,
                "database_schema": str(self.database_schema),
                "pipeline_plan": pipeline_plan,
                "detected_language": detected_language,
                "agent_results": agent_results,
                "relevant_schema_content": relevant_schema_content or "No relevant schema content provided"
            })
            return response.get("output", "No se pudieron combinar los resultados.")
        except Exception as e:
            return f"Error al combinar resultados: {str(e)}" 