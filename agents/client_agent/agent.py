from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_openai_tools_agent
from .prompt import CLIENT_AGENT_PROMPT
from config.settings import settings
from ..registry import BaseAgent, register_agent
from tools.sqlserver_database_tool import SQLServerDatabaseTool
from typing import Dict, Any

@register_agent("ClientAgent")
class ClientAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=settings.OPENAI_KEY
        )
        
        # Initialize SQL Server database tool
        self.db_tool = SQLServerDatabaseTool(llm=self.llm)
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_template(CLIENT_AGENT_PROMPT)
        
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
            # Usar SOLO el contenido relevante del schema
            if relevant_schema_content and relevant_schema_content != "No relevant schema content provided":
                schema_context = relevant_schema_content
            else:
                schema_context = "No relevant schema content available"
            
            # Use our custom agent with the relevant schema content only
            response = self.agent_executor.invoke({
                "user_input": user_input,
                "database_schema": schema_context,
                "relevant_schema_content": relevant_schema_content or "No relevant schema content provided"
            })
            return response.get("output", "No se pudo obtener respuesta de la base de datos.")
        except Exception as e:
            return f"Error al procesar la consulta de clientes: {str(e)}"
    
    def analyze_clients(self, user_input: str) -> str:
        """Método específico para análisis de clientes"""
        return self.run(user_input) 