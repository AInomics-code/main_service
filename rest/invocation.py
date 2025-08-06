from fastapi import Request
from pydantic import BaseModel
from agents.graph import DynamicAgentGraph
from services.chat_history import chat_history_service
import threading

class ServiceManager:
    """Singleton para manejar la inicialización de servicios con sistema híbrido"""
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
        """Inicializa servicios costosos al startup con sistema híbrido"""
        if self._initialized:
            return self._graph
        
        with self._lock:
            if self._initialized:  # Double-check locking
                return self._graph
            
            print("🚀 Inicializando servicios de IA con sistema híbrido...")
            
            # Pre-inicializar LLMs críticos
            print("🔄 Pre-cargando LLMs críticos...")
            from config.hybrid_llm_manager import hybrid_llm_manager
            hybrid_llm_manager.preload_critical_agents()
            
            # Mostrar información de LLMs cargados
            loaded_agents = hybrid_llm_manager.get_loaded_agents()
            print("✅ LLMs cargados:")
            for agent, info in loaded_agents.items():
                print(f"   - {agent}: {info}")
            
            # Pre-inicializar el grafo
            print("🔄 Inicializando DynamicAgentGraph...")
            self._graph = DynamicAgentGraph()
            
            # Pre-cargar agente crítico (StrategyAgent)
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
    session_id: str = None

async def invoke_agent(request: Request):
    try:
        body = await request.json()
        user_request = UserRequest(**body)
        
        # Manejar session_id
        session_id = user_request.session_id
        
        # Si no hay session_id, crear una nueva sesión
        if not session_id:
            session_id = chat_history_service.create_session()
            print(f"🆕 Nueva sesión creada: {session_id}")
        else:
            # Verificar si la sesión existe
            if not chat_history_service.session_exists(session_id):
                session_id = chat_history_service.create_session()
                print(f"🔄 Sesión no encontrada, nueva sesión creada: {session_id}")
        
        # Obtener el grafo (se inicializa automáticamente si es necesario)
        graph = _service_manager.get_graph()
        
        # Obtener historial de la sesión para contexto
        chat_history = chat_history_service.get_history(session_id, limit=5)
        
        # Construir contexto con historial si existe
        context_message = user_request.message
        if chat_history:
            # Crear contexto con los últimos mensajes
            context_parts = []
            for msg in reversed(chat_history):  # Invertir para orden cronológico
                context_parts.append(f"Usuario: {msg['user_message']}")
                context_parts.append(f"IA: {msg['ai_response']}")
            
            context_parts.append(f"Usuario: {user_request.message}")
            context_message = "\n".join(context_parts)
            print(f"📝 Usando historial de {len(chat_history)} mensajes para contexto")
        
        # Usar instancia del grafo con contexto y historial
        result = graph.process(user_request.message, chat_history)
        
        # Preparar respuesta base
        response_data = {
            "success": True,
            "message": user_request.message,
            "session_id": session_id,
            "has_history": len(chat_history) > 0
        }
        
        # Si necesita clarificación, no guardar en historial aún
        if result.get("type") == "clarification_needed":
            response_data.update({
                "result": result,  # Ahora siempre es la estructura completa
                "needs_clarification": True,
                "clarification_questions": result.get("clarification_questions", []),
                "reason": result.get("reason")
            })
        else:
            # Guardar el mensaje y respuesta en el historial solo si no necesitaba clarificación
            metadata = {
                "original_message": user_request.message,
                "has_context": len(chat_history) > 0,
                "context_length": len(chat_history)
            }
            
            chat_history_service.add_message(
                session_id=session_id,
                message=user_request.message,
                response=result.get("final_response", str(result)),
                metadata=metadata
            )
            
            # Obtener información de la sesión
            session_info = chat_history_service.get_session_info(session_id)
            
            response_data.update({
                "result": result,
                "session_info": session_info,
                "needs_clarification": False
            })
        
        return response_data
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error processing request"
        }
