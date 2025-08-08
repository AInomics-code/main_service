from fastapi import APIRouter, Request, HTTPException
from rest.invocation import invoke_agent
from services.chat_history import chat_history_service

router = APIRouter(prefix="/api/v1")

@router.post("/invoke")
async def invoke(request: Request):
    return await invoke_agent(request)
    """Crear una nueva sesión de chat"""
    try:
        session_id = chat_history_service.create_session()
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Session created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")