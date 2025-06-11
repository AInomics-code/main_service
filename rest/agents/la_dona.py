from fastapi import Request
import logging
from ..tools.database_tool import DatabaseTool
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
import os
from config.settings import settings

logger = logging.getLogger(__name__)

# Initialize LLM with API key from settings
llm = ChatOpenAI(
    model="gpt-4", 
    temperature=0,
    openai_api_key=settings.OPENAI_KEY
)

# Initialize database tool with LLM
db_tool = DatabaseTool(llm=llm)

async def process(request: Request):
    try:
        body = await request.json()
        logger.debug(f"Received request body: {body}")
        
        # Get the query from the request body
        query = body.get("query")
        if not query:
            return {"error": "No query provided in request body"}

        tools = db_tool.get_tools()
        
        prompt_prefix = """
You are a professional retail analyst with expertise in sales performance, customer insights, and product analytics.
Your role is to serve sales departments and management teams by providing data-driven insights and actionable recommendations.
Always base your responses on concrete data and analytics, presenting findings in a professional and courteous manner.
Structure your responses to include: key findings, data-backed insights, and specific next steps or recommendations for action.
Maintain a respectful, helpful, and service-oriented approach in all interactions.
Communicate complex analytics in clear business language that sales teams and executives can immediately understand and act upon.

IMPORTANT: Never show technical IDs or database identifiers in your responses. Always look for and present descriptive information such as:
- Customer names instead of customer IDs
- Product names, categories, or descriptions instead of product IDs  
- Store names or locations instead of store IDs
- Any other human-readable identifiers instead of technical codes
When presenting data, focus on meaningful business identifiers that managers and sales teams can recognize and act upon.

Always respond in the same language as the query to ensure clear communication with your stakeholders.
"""

        agent_executor = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,
            handle_parsing_errors=True,
            agent_kwargs={"prefix": prompt_prefix}
        )

        # Execute the agent with the query from the request
        response = agent_executor.run(query)
        
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {"error": str(e)}