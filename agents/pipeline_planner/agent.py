from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from .prompt import PIPELINE_PLANNER_PROMPT
from config.settings import settings
from config.hybrid_llm_manager import hybrid_llm_manager
from config.hybrid_llm_config import AGENT_CONFIG
import json

class PipelinePlannerAgent:
    def __init__(self):
        # Usar el manager híbrido para obtener LLM especializado
        self.llm = hybrid_llm_manager.get_llm_for_agent("PipelinePlanner")
        self.prompt = ChatPromptTemplate.from_template(PIPELINE_PLANNER_PROMPT)
        
        # Obtener configuración de agentes disponibles
        self.available_agents = list(AGENT_CONFIG.keys())
        self.default_agent = "StrategyAgent"  # Agente por defecto
    
    def _validate_and_fix_pipeline(self, pipeline: list) -> list:
        if not pipeline or not isinstance(pipeline, list):
            return [[self.default_agent]]  # NO agregar Supervisor aquí
        
        if len(pipeline) == 1 and len(pipeline[0]) == 1:
            single_agent = pipeline[0][0]
            if single_agent in self.available_agents:
                return pipeline  # NO agregar Supervisor aquí
        
        # Validar que todos los agentes existan
        validated_pipeline = []
        for step in pipeline:
            validated_step = [agent for agent in step if agent in self.available_agents]
            if validated_step:
                validated_pipeline.append(validated_step)
        
        # Asegurar que el agente por defecto esté al final (antes del supervisor)
        if not validated_pipeline:
            validated_pipeline = [[self.default_agent]]
        elif self.default_agent not in validated_pipeline[-1]:
            validated_pipeline.append([self.default_agent])
        
        # NO agregar el Supervisor automáticamente - el grafo ya tiene un nodo supervisor final
        # El Supervisor se ejecutará en el nodo supervisor del grafo, no en el pipeline
        
        return validated_pipeline
    
    def plan_pipeline(self, user_question: str) -> dict:
        try:
            chain = self.prompt | self.llm
            response = chain.invoke({"user_question": user_question})
            
            try:
                result = json.loads(response.content.strip())
                if "pipeline" not in result:
                    return {
                        "pipeline": [[self.default_agent]],
                        "error": "Respuesta no contiene clave 'pipeline'"
                    }
                
                result["pipeline"] = self._validate_and_fix_pipeline(result["pipeline"])
                return result
                
            except json.JSONDecodeError:
                print(f"Error: {response.content}")
                return {
                    "pipeline": [[self.default_agent]],
                    "error": "No se pudo parsear la respuesta como JSON"
                }
                
        except Exception as e:
            return {
                "pipeline": [[self.default_agent]],
                "error": f"Error en el agente: {str(e)}"
            } 