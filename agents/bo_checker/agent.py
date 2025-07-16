from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType
from .prompt import BO_CHECKER_PROMPT
from config.settings import settings
from ..registry import BaseAgent, register_agent
from tools.sqlserver_database_tool import SQLServerDatabaseTool

@register_agent("BOChecker")
class BOCheckerAgent(BaseAgent):
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
        
        # print(self.database_schema)
        
        # Create SQL agent with database tools
        self.sql_agent = create_sql_agent(
            llm=self.llm,
            toolkit=self.db_tool,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False
        )
        
        # Create prompt template with database schema
        self.prompt = ChatPromptTemplate.from_template(BO_CHECKER_PROMPT)
    
    def run(self, user_input: str) -> str:
        """Método estándar que implementa la interfaz BaseAgent"""
        try:
            # First, try to use the SQL agent for database queries
            if any(keyword in user_input.lower() for keyword in ['back order', 'backorder', 'inventory', 'stock', 'order', 'delivery']):
                # Use SQL agent for database-related queries
                response = self.sql_agent.invoke({"input": user_input})
                return response.get("output", "No se pudo obtener respuesta de la base de datos.")
            else:
                # Use regular prompt for general questions
                chain = self.prompt | self.llm
                response = chain.invoke({
                    "user_input": user_input,
                    "database_schema": str(self.database_schema)
                })
                return response.content.strip()
        except Exception as e:
            return f"Error al procesar la consulta: {str(e)}"
    
    def check_back_orders(self, user_input: str) -> str:
        """Método específico mantenido para compatibilidad"""
        return self.run(user_input) 