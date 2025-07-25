from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_openai_tools_agent
from .prompt import STRATEGY_AGENT_PROMPT
from config.settings import settings
from ..registry import BaseAgent, register_agent
from tools.sqlserver_database_tool import SQLServerDatabaseTool

@register_agent("StrategyAgent")
class StrategyAgent(BaseAgent):
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
        self.prompt = ChatPromptTemplate.from_template(STRATEGY_AGENT_PROMPT)
        
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
                "database_schema": str(self.database_schema),
                "agent_results": "No previous agent results available"
            })
            return response.get("output", "No se pudo obtener respuesta de la base de datos.")
        except Exception as e:
            return f"Error al procesar la consulta estratégica: {str(e)}"
    
    def synthesize_results(self, user_input: str, agent_results: str) -> str:
        """Método específico para síntesis de resultados de otros agentes"""
        try:
            response = self.agent_executor.invoke({
                "user_input": user_input,
                "database_schema": str(self.database_schema),
                "agent_results": agent_results
            })
            return response.get("output", "No se pudo sintetizar los resultados.")
        except Exception as e:
            return f"Error al sintetizar resultados: {str(e)}"
    
    def provide_strategic_insights(self, user_input: str) -> str:
        """Método específico para insights estratégicos"""
        return self.run(user_input) 