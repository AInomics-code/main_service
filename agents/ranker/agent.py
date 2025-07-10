from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from .prompt import RANKER_PROMPT
from config.settings import settings
from ..registry import BaseAgent, register_agent

@register_agent("Ranker")
class RankerAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=settings.OPENAI_KEY
        )
        self.prompt = ChatPromptTemplate.from_template(RANKER_PROMPT)
    
    def run(self, user_input: str) -> str:
        """Método estándar que implementa la interfaz BaseAgent"""
        chain = self.prompt | self.llm
        response = chain.invoke({"user_input": user_input})
        return response.content.strip()
    
    def rank_data(self, user_input: str) -> str:
        """Método específico mantenido para compatibilidad"""
        return self.run(user_input) 