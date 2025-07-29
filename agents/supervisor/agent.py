from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_openai_tools_agent
from .prompt import SUPERVISOR_PROMPT
from ..registry import BaseAgent, register_agent
from tools.database_singleton import database_singleton
from typing import Dict, Any

@register_agent("Supervisor")
class SupervisorAgent(BaseAgent):
    def __init__(self):
        # Usar singleton para LLM y herramientas de base de datos
        self.llm = database_singleton.get_llm()
        self.db_tool = database_singleton.get_database_tool()
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_template(SUPERVISOR_PROMPT)
        
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
            max_iterations=6,  # Máximo 6 iteraciones para evitar loops infinitos
            early_stopping_method="generate",  # Para temprano cuando se genera una respuesta
            handle_parsing_errors=True  # Manejo de errores de parsing
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
            return f"Error al procesar la consulta: {str(e)}"
    
    def combine_results(self, user_input: str, pipeline_plan: str, detected_language: str, agent_results: str, relevant_schema_content: str = None) -> str:
        """Método específico para combinar resultados"""
        try:
            # Usar SOLO el contenido relevante del schema
            if relevant_schema_content and relevant_schema_content != "No relevant schema content provided":
                schema_context = relevant_schema_content
            else:
                schema_context = "No relevant schema content available"
            
            response = self.agent_executor.invoke({
                "user_input": user_input,
                "database_schema": schema_context,
                "pipeline_plan": pipeline_plan,
                "detected_language": detected_language,
                "agent_results": agent_results,
                "relevant_schema_content": relevant_schema_content or "No relevant schema content provided"
            })
            return response.get("output", "No se pudieron combinar los resultados.")
        except Exception as e:
            return f"Error al combinar resultados: {str(e)}" 