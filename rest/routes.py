from fastapi import APIRouter, Request
from rest.invocation import invoke_agent
from agents.registry import list_available_agents

router = APIRouter(prefix="/api/v1")

@router.post("/invoke")
async def invoke(request: Request):
    return await invoke_agent(request)

@router.get("/agents")
async def list_agents():
    """Endpoint para listar todos los agentes disponibles"""
    agents = list_available_agents()
    return {
        "success": True,
        "agents": agents,
        "count": len(agents)
    }