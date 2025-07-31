from langchain.prompts import ChatPromptTemplate
from .prompt import SUPERVISOR_PROMPT
from ..base_agent import BaseAgent
from ..registry import register_agent
from typing import Dict, Any
from config.hybrid_llm_manager import hybrid_llm_manager

@register_agent("Supervisor")
class SupervisorAgent(BaseAgent):
    def __init__(self):
        super().__init__("Supervisor")
        # Obtener LLM para síntesis sin herramientas
        self.synthesis_llm = hybrid_llm_manager.get_llm_for_agent("Supervisor")
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Crear el prompt template específico del SupervisorAgent"""
        return ChatPromptTemplate.from_template(SUPERVISOR_PROMPT)
    
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
        """Método específico para combinar resultados usando solo síntesis"""
        try:
            # Usar SOLO el contenido relevante del schema
            if relevant_schema_content and relevant_schema_content != "No relevant schema content provided":
                schema_context = relevant_schema_content
            else:
                schema_context = "No relevant schema content available"
            
            # Usar el ChatPromptTemplate correctamente
            prompt = self._create_prompt()
            
            # Formatear el prompt con las variables correctas
            formatted_prompt = prompt.format_messages(
                relevant_schema_content=schema_context,
                user_input=user_input,
                detected_language=detected_language,
                pipeline_plan=pipeline_plan,
                agent_results=agent_results,
                agent_scratchpad=""
            )
            
            # Usar LLM directamente para síntesis sin herramientas
            response = self.synthesis_llm.invoke(formatted_prompt)
            return response.content
            
        except Exception as e:
            return f"Error al combinar resultados: {str(e)}" 