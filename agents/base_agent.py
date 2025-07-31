from abc import ABC, abstractmethod
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_openai_tools_agent
from typing import Dict, Any, List
from config.hybrid_llm_manager import hybrid_llm_manager
from config.hybrid_llm_config import AGENT_CONFIG
from tools.tool_manager import tool_manager

class BaseAgent(ABC):
    """
    Clase base para todos los agentes con sistema híbrido de LLMs
    """
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        
        # Obtener LLM apropiado (compartido o especializado)
        self.llm = hybrid_llm_manager.get_llm_for_agent(agent_name)
        
        # Obtener configuración específica del agente
        self.agent_config = AGENT_CONFIG.get(agent_name, {
            "max_iterations": 3,
            "max_execution_time": 30,
            "early_stopping_method": "force"
        })
        
        # Obtener herramientas del tool manager
        self.tools = tool_manager.get_default_tools()
        
        # Crear prompt template (debe ser implementado por subclases)
        self.prompt = self._create_prompt()
        
        # Crear agente con herramientas
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Crear executor con configuración específica
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=self.agent_config["max_iterations"],
            max_execution_time=self.agent_config["max_execution_time"],
            early_stopping_method=self.agent_config["early_stopping_method"],
            handle_parsing_errors=True,
            return_intermediate_steps=True,
            trim_intermediate_steps=-1
        )
    
    @abstractmethod
    def _create_prompt(self) -> ChatPromptTemplate:
        """Crear el prompt template específico del agente"""
        pass
    
    def run(self, user_input: str, database_schema: Dict[str, Any] = None, relevant_schema_content: str = None) -> str:
        """Método estándar para ejecutar el agente"""
        try:
            # Usar contenido relevante del schema si está disponible
            if relevant_schema_content and relevant_schema_content != "No relevant schema content provided":
                schema_context = relevant_schema_content
            else:
                schema_context = "No relevant schema content available"
            
            # Ejecutar agente
            response = self.agent_executor.invoke({
                "user_input": user_input,
                "database_schema": schema_context,
                "relevant_schema_content": relevant_schema_content or "No relevant schema content provided"
            })
            
            return response.get("output", "No se pudo obtener respuesta del agente.")
            
        except Exception as e:
            return f"Error al procesar la consulta en {self.agent_name}: {str(e)}"
    
    def add_tools(self, tools: List):
        """Agregar herramientas adicionales al agente"""
        self.tools.extend(tools)
        # Recrear agente con nuevas herramientas
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=self.agent_config["max_iterations"],
            max_execution_time=self.agent_config["max_execution_time"],
            early_stopping_method=self.agent_config["early_stopping_method"],
            handle_parsing_errors=True,
            return_intermediate_steps=True,
            trim_intermediate_steps=-1
        )
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Obtener información del agente"""
        return {
            "name": self.agent_name,
            "llm_model": self.llm.model_name,
            "llm_temperature": self.llm.temperature,
            "max_iterations": self.agent_config["max_iterations"],
            "max_execution_time": self.agent_config["max_execution_time"],
            "tools_count": len(self.tools),
            "tools": [tool.name for tool in self.tools]
        } 