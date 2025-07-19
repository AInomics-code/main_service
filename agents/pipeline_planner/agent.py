from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from .prompt import PIPELINE_PLANNER_PROMPT
from config.settings import settings
import json

class PipelinePlannerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=settings.OPENAI_KEY
        )
        self.prompt = ChatPromptTemplate.from_template(PIPELINE_PLANNER_PROMPT)
    
    def _validate_and_fix_pipeline(self, pipeline: list) -> list:
        if not pipeline or not isinstance(pipeline, list):
            return [["StrategyAgent"]]
        
        if len(pipeline) == 1 and len(pipeline[0]) == 1:
            single_agent = pipeline[0][0]
            if single_agent in ["StrategyAgent"]:
                return pipeline
        
        last_step = pipeline[-1] if pipeline else []
        has_strategy = "StrategyAgent" in last_step
        
        if not has_strategy:
            if last_step and any(agent != "StrategyAgent" for agent in last_step):
                pipeline.append(["StrategyAgent"])
            else:
                pipeline[-1] = ["StrategyAgent"]
        
        return pipeline
    
    def plan_pipeline(self, user_question: str) -> dict:
        try:
            chain = self.prompt | self.llm
            response = chain.invoke({"user_question": user_question})
            
            try:
                result = json.loads(response.content.strip())
                if "pipeline" not in result:
                    return {
                        "pipeline": [["StrategyAgent"]],
                        "error": "Respuesta no contiene clave 'pipeline'"
                    }
                
                result["pipeline"] = self._validate_and_fix_pipeline(result["pipeline"])
                return result
                
            except json.JSONDecodeError:
                print(f"Error: {response.content}")
                return {
                    "pipeline": [["StrategyAgent"]],
                    "error": "No se pudo parsear la respuesta como JSON"
                }
                
        except Exception as e:
            return {
                "pipeline": [["StrategyAgent"]],
                "error": f"Error en el agente: {str(e)}"
            } 