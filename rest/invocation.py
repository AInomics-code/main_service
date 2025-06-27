from fastapi import Request
from pydantic import BaseModel
from agents.graph import ParallelAgentGraph

class UserRequest(BaseModel):
    message: str

async def invoke_agent(request: Request):
    try:
        body = await request.json()
        user_request = UserRequest(**body)
        
        graph = ParallelAgentGraph()
        
        result = graph.process(user_request.message)
        
        return {
            "success": True,
            "result": result,
            "message": user_request.message
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error processing request"
        }
