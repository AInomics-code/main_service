from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_openai_tools_agent
from .prompt import STRATEGY_AGENT_PROMPT
from ..registry import BaseAgent, register_agent
from tools.database_singleton import database_singleton
from typing import Dict, Any

@register_agent("StrategyAgent")
class StrategyAgent(BaseAgent):
    def __init__(self):
        # Usar singleton para LLM y herramientas de base de datos
        self.llm = database_singleton.get_llm()
        self.db_tool = database_singleton.get_database_tool()
        
        # Protection against infinite loops
        self.query_history = set()  # Track executed queries
        self.max_query_attempts = 1
        self.query_count = 0
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_template(STRATEGY_AGENT_PROMPT)
        
        # Create custom agent with database tools and our prompt
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.db_tool.get_tools(),
            prompt=self.prompt
        )
        
        # Create agent executor with limits to prevent infinite loops
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.db_tool.get_tools(),
            verbose=True,
            max_iterations=3,  # Reduce a 3 iteraciones máximo
            max_execution_time=30,  # Tiempo máximo de 30 segundos
            early_stopping_method="force",  # Cambia a "force" en lugar de "generate"
            handle_parsing_errors=True,
            return_intermediate_steps=True,  # Para debug
            # Configuración adicional para prevenir loops
            trim_intermediate_steps=-1  # Mantiene solo el último paso
        )
    
    def run(self, user_input: str, database_schema: Dict[str, Any] = None, relevant_schema_content: str = None) -> str:
        """Método estándar que implementa la interfaz BaseAgent con protección contra loops"""
        # Reset counters for new execution
        self.query_count = 0
        self.query_history.clear()
        
        try:
            # Import callback class for loop protection
            from langchain.callbacks import BaseCallbackHandler
            
            class LoopProtectionCallback(BaseCallbackHandler):
                def __init__(self, agent_instance):
                    self.agent = agent_instance
                
                def on_tool_start(self, serialized, input_str, **kwargs):
                    """Intercepta cuando se va a usar una herramienta"""
                    if "sql_db_query" in str(serialized.get("name", "")):
                        self.agent.query_count += 1
                        query = str(input_str)
                        
                        # Prevenir queries repetidas
                        if query in self.agent.query_history:
                            raise Exception(f"Query repetida detectada - deteniendo ejecución. Query: {query[:100]}...")
                        
                        # Prevenir más de N queries
                        if self.agent.query_count > self.agent.max_query_attempts:
                            raise Exception(f"Máximo número de queries ({self.agent.max_query_attempts}) excedido - deteniendo ejecución")
                        
                        self.agent.query_history.add(query)
                        print(f"[StrategyAgent] Ejecutando query #{self.agent.query_count}: {query[:100]}...")
            
            # Usar SOLO el contenido relevante del schema
            if relevant_schema_content and relevant_schema_content != "No relevant schema content provided":
                schema_context = relevant_schema_content
            else:
                schema_context = "No relevant schema content available"
            
            # Create callback instance
            callback = LoopProtectionCallback(self)
            
            # Use our custom agent with the relevant schema content only
            response = self.agent_executor.invoke({
                "user_input": user_input,
                "database_schema": schema_context,
                "agent_results": "No previous agent results available",
                "relevant_schema_content": relevant_schema_content or "No relevant schema content provided"
            }, config={"callbacks": [callback]})
            
            return response.get("output", "No se pudo obtener respuesta de la base de datos.")
            
        except Exception as e:
            if "Query repetida" in str(e) or "Máximo número" in str(e):
                return f"Análisis estratégico completado. {str(e)}"
            return f"Error al procesar la consulta estratégica: {str(e)}"
    
    def synthesize_results(self, user_input: str, agent_results: str, database_schema: Dict[str, Any] = None, relevant_schema_content: str = None) -> str:
        """Método específico para síntesis de resultados de otros agentes con protección contra loops"""
        # Reset counters for new execution
        self.query_count = 0
        self.query_history.clear()
        
        try:
            # Import callback class for loop protection
            from langchain.callbacks import BaseCallbackHandler
            
            class LoopProtectionCallback(BaseCallbackHandler):
                def __init__(self, agent_instance):
                    self.agent = agent_instance
                
                def on_tool_start(self, serialized, input_str, **kwargs):
                    """Intercepta cuando se va a usar una herramienta"""
                    if "sql_db_query" in str(serialized.get("name", "")):
                        self.agent.query_count += 1
                        query = str(input_str)
                        
                        # Prevenir queries repetidas
                        if query in self.agent.query_history:
                            raise Exception(f"Query repetida detectada - deteniendo ejecución. Query: {query[:100]}...")
                        
                        # Prevenir más de N queries
                        if self.agent.query_count > self.agent.max_query_attempts:
                            raise Exception(f"Máximo número de queries ({self.agent.max_query_attempts}) excedido - deteniendo ejecución")
                        
                        self.agent.query_history.add(query)
                        print(f"[StrategyAgent] Síntesis - Ejecutando query #{self.agent.query_count}: {query[:100]}...")
            
            # Usar SOLO el contenido relevante del schema
            if relevant_schema_content and relevant_schema_content != "No relevant schema content provided":
                schema_context = relevant_schema_content
            else:
                schema_context = "No relevant schema content available"
            
            # Create callback instance
            callback = LoopProtectionCallback(self)
            
            response = self.agent_executor.invoke({
                "user_input": user_input,
                "database_schema": schema_context,
                "agent_results": agent_results,
                "relevant_schema_content": relevant_schema_content or "No relevant schema content provided"
            }, config={"callbacks": [callback]})
            
            return response.get("output", "No se pudo sintetizar los resultados.")
            
        except Exception as e:
            if "Query repetida" in str(e) or "Máximo número" in str(e):
                return f"Síntesis estratégica completada. {str(e)}"
            return f"Error al sintetizar resultados: {str(e)}"
    
    def provide_strategic_insights(self, user_input: str) -> str:
        """Método específico para insights estratégicos"""
        return self.run(user_input) 