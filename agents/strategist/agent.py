from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from .prompt import STRATEGIST_PROMPT
from config.settings import settings
from ..registry import BaseAgent, register_agent

@register_agent("Strategist")
class StrategistAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            openai_api_key=settings.OPENAI_KEY
        )
        self.prompt = ChatPromptTemplate.from_template(STRATEGIST_PROMPT)
    
    def run(self, user_input: str) -> str:
        """Método estándar que implementa la interfaz BaseAgent"""
        # Para el strategist, necesitamos manejar los resultados de otros agentes
        # Por ahora, usamos un placeholder
        chain = self.prompt | self.llm
        response = chain.invoke({
            "user_input": user_input,
            "agent_results": "Resultados de agentes previos"
        })
        return response.content.strip()
    
    def synthesize_results(self, user_input: str, agent_results: str) -> str:
        """Método específico para síntesis de resultados"""
        chain = self.prompt | self.llm
        response = chain.invoke({
            "user_input": user_input,
            "agent_results": agent_results
        })
        return response.content.strip() 