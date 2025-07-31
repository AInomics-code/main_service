from fastapi import APIRouter, Request, HTTPException
from rest.invocation import invoke_agent
from agents.registry import list_available_agents
from services.chat_history import chat_history_service

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

@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 10):
    """Obtener historial de chat para una sesión específica"""
    try:
        if not chat_history_service.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        
        history = chat_history_service.get_history(session_id, limit=limit)
        session_info = chat_history_service.get_session_info(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "session_info": session_info,
            "history": history,
            "count": len(history)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")

@router.get("/chat/session/{session_id}")
async def get_session_info(session_id: str):
    """Obtener información de una sesión específica"""
    try:
        session_info = chat_history_service.get_session_info(session_id)
        
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "session_id": session_id,
            "session_info": session_info
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session info: {str(e)}")

@router.delete("/chat/session/{session_id}")
async def delete_session(session_id: str):
    """Eliminar una sesión y todo su historial"""
    try:
        if not chat_history_service.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        
        success = chat_history_service.delete_session(session_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete session")
        
        return {
            "success": True,
            "message": "Session deleted successfully",
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

@router.post("/chat/session")
async def create_session():
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