from langchain.prompts import ChatPromptTemplate
from .prompt import LANGUAGE_DETECTION_PROMPT
from config.hybrid_llm_manager import hybrid_llm_manager

class LanguageDetectorAgent:
    def __init__(self):
        # Usar el manager híbrido para obtener LLM especializado (gpt-3.5-turbo)
        self.llm = hybrid_llm_manager.get_llm_for_agent("LanguageDetector")
        self.prompt = ChatPromptTemplate.from_template(LANGUAGE_DETECTION_PROMPT)
    
    def detect_language(self, user_input: str) -> str:
        chain = self.prompt | self.llm
        response = chain.invoke({"user_input": user_input})
        return response.content.strip() 