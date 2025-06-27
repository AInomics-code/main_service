from fastapi import APIRouter, Request
from rest.invocation import invoke_agent

router = APIRouter(prefix="/api/v1")

@router.post("/invoke")
async def invoke(request: Request):
    return await invoke_agent(request)