from langchain.prompts import ChatPromptTemplate
from .prompt import CLIENT_AGENT_PROMPT
from ..base_agent import BaseAgent
from ..registry import register_agent
from typing import Dict, Any

@register_agent("ClientAgent")
class ClientAgent(BaseAgent):
    def __init__(self):
        super().__init__("ClientAgent")
        self.query_history = set()
        self.max_query_attempts = 1
        self.query_count = 0
        
    def _create_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_template(CLIENT_AGENT_PROMPT)
    
    def run(self, user_input: str, database_schema: Dict[str, Any] = None, relevant_schema_content: str = None) -> str:
        self.query_count = 0
        self.query_history.clear()
        try:
            from langchain.callbacks import BaseCallbackHandler
            class LoopProtectionCallback(BaseCallbackHandler):
                def __init__(self, agent_instance):
                    self.agent = agent_instance
                def on_tool_start(self, serialized, input_str, **kwargs):
                    if "simple_database_query" in str(serialized.get("name", "")):
                        self.agent.query_count += 1
                        query = str(input_str)
                        if query in self.agent.query_history:
                            raise Exception(f"Query repetida detectada - deteniendo ejecución. Query: {query[:100]}...")
                        if self.agent.query_count > self.agent.max_query_attempts:
                            raise Exception(f"Máximo número de queries ({self.agent.max_query_attempts}) excedido - deteniendo ejecución")
                        self.agent.query_history.add(query)
                        print(f"[ClientAgent] Ejecutando query #{self.agent.query_count}: {query[:100]}...")
            callback = LoopProtectionCallback(self)
            if relevant_schema_content and relevant_schema_content != "No relevant schema content provided":
                schema_context = relevant_schema_content
            else:
                schema_context = "No relevant schema content available"
            response = self.agent_executor.invoke({
                "user_input": user_input,
                "database_schema": schema_context,
                "relevant_schema_content": relevant_schema_content or "No relevant schema content provided"
            }, config={"callbacks": [callback]})
            return response.get("output", "No se pudo obtener respuesta de la base de datos.")
        except Exception as e:
            if "Query repetida" in str(e) or "Máximo número" in str(e):
                return f"Análisis de clientes completado. {str(e)}"
            return f"Error al procesar la consulta de clientes: {str(e)}"
    
    def analyze_clients(self, user_input: str) -> str:
        return self.run(user_input) 