from langchain.prompts import ChatPromptTemplate
from .prompt import FIELD_OPS_AGENT_PROMPT
from ..base_agent import BaseAgent
from ..registry import register_agent
from typing import Dict, Any

@register_agent("FieldOpsAgent")
class FieldOpsAgent(BaseAgent):
    def __init__(self):
        super().__init__("FieldOpsAgent")
    
    def _create_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_template(FIELD_OPS_AGENT_PROMPT)
    
    def run(self, user_input: str, database_schema: Dict[str, Any] = None, relevant_schema_content: str = None) -> str:
        try:
            if relevant_schema_content and relevant_schema_content != "No relevant schema content provided":
                schema_context = relevant_schema_content
            else:
                schema_context = "No relevant schema content available"
            response = self.agent_executor.invoke({
                "user_input": user_input,
                "database_schema": schema_context,
                "relevant_schema_content": relevant_schema_content or "No relevant schema content provided"
            })
            return response.get("output", "No se pudo obtener respuesta de la base de datos.")
        except Exception as e:
            return f"Error al procesar la consulta de operaciones de campo: {str(e)}"
    
    def analyze_field_ops(self, user_input: str) -> str:
        return self.run(user_input) 