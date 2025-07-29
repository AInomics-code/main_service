from fastapi import Request
from pydantic import BaseModel
from agents.graph import DynamicAgentGraph

# Variables globales para instancias pre-inicializadas
_graph = None

def initialize_services():
    """Inicializa servicios costosos al startup"""
    global _graph
    
    print("🚀 Inicializando servicios de IA...")
    
    # Pre-inicializar solo el grafo (los agentes se cargarán lazy)
    print("🔄 Inicializando DynamicAgentGraph...")
    _graph = DynamicAgentGraph()
    
    # Pre-cargar solo el agente más común (StrategyAgent)
    print("🔄 Pre-cargando agente crítico (StrategyAgent)...")
    from agents.registry import preload_agent
    preload_agent("StrategyAgent")
    
    print("✅ Servicios inicializados correctamente")

class UserRequest(BaseModel):
    message: str

async def invoke_agent(request: Request):
    try:
        body = await request.json()
        user_request = UserRequest(**body)
        
        # Usar instancia global pre-inicializada
        result = _graph.process(user_request.message)
        
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

# Inicializar servicios al importar el módulo
initialize_services()
