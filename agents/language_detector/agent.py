from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from .prompt import LANGUAGE_DETECTION_PROMPT
from config.settings import settings

class LanguageDetectorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=settings.OPENAI_KEY
        )
        self.prompt = ChatPromptTemplate.from_template(LANGUAGE_DETECTION_PROMPT)
    
    def detect_language(self, user_input: str) -> str:
        chain = self.prompt | self.llm
        response = chain.invoke({"user_input": user_input})
        return response.content.strip() 