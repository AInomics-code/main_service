from fastapi import Request
from pydantic import BaseModel
from agents.graph import DynamicAgentGraph
from schema_summarizer.schema_summarizer import SchemaSummarizer

# Variables globales para instancias pre-inicializadas
_schema_summarizer = None
_graph = None

def initialize_services():
    """Inicializa servicios costosos al startup"""
    global _schema_summarizer, _graph
    
    print("🚀 Inicializando servicios de IA...")
    
    # Pre-inicializar SchemaSummarizer (carga modelo y embeddings)
    print("📚 Inicializando SchemaSummarizer...")
    _schema_summarizer = SchemaSummarizer()
    
    # Pre-inicializar DynamicAgentGraph
    print("🔄 Inicializando DynamicAgentGraph...")
    _graph = DynamicAgentGraph()
    
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
