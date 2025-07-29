from fastapi import Request
from pydantic import BaseModel
from agents.graph import DynamicAgentGraph
import threading

class ServiceManager:
    """Singleton para manejar la inicialización de servicios"""
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_graph'):
            self._graph = None
    
    def initialize_services(self):
        """Inicializa servicios costosos al startup"""
        if self._initialized:
            return self._graph
        
        with self._lock:
            if self._initialized:  # Double-check locking
                return self._graph
            
            print("🚀 Inicializando servicios de IA...")
            
            # Pre-inicializar solo el grafo (los agentes se cargarán lazy)
            print("🔄 Inicializando DynamicAgentGraph...")
            self._graph = DynamicAgentGraph()
            
            # Pre-cargar solo el agente más común (StrategyAgent)
            print("🔄 Pre-cargando agente crítico (StrategyAgent)...")
            from agents.registry import preload_agent
            preload_agent("StrategyAgent")
            
            print("✅ Servicios inicializados correctamente")
            self._initialized = True
            return self._graph
    
    def get_graph(self):
        """Obtiene la instancia del grafo, inicializando si es necesario"""
        if not self._initialized:
            return self.initialize_services()
        return self._graph

# Instancia global del manager
_service_manager = ServiceManager()

class UserRequest(BaseModel):
    message: str

async def invoke_agent(request: Request):
    try:
        body = await request.json()
        user_request = UserRequest(**body)
        
        # Obtener el grafo (se inicializa automáticamente si es necesario)
        graph = _service_manager.get_graph()
        
        # Usar instancia del grafo
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
