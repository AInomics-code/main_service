from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from .prompt import SUPERVISOR_PROMPT
from config.settings import settings

class SupervisorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            openai_api_key=settings.OPENAI_KEY
        )
        self.prompt = ChatPromptTemplate.from_template(SUPERVISOR_PROMPT)
    
    def combine_results(self, user_input: str, pipeline_plan: str, detected_language: str, agent_results: str) -> str:
        chain = self.prompt | self.llm
        response = chain.invoke({
            "user_input": user_input,
            "pipeline_plan": pipeline_plan,
            "detected_language": detected_language,
            "agent_results": agent_results
        })
        return response.content.strip() 