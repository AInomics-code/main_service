from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from .prompt import TASK_CLASSIFICATION_PROMPT
from config.settings import settings

class TaskClassifierAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=settings.OPENAI_KEY
        )
        self.prompt = ChatPromptTemplate.from_template(TASK_CLASSIFICATION_PROMPT)
    
    def classify_task(self, user_question: str) -> str:
        chain = self.prompt | self.llm
        response = chain.invoke({"user_question": user_question})
        return response.content.strip() 