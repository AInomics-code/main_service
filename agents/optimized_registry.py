from typing import Dict, Type, Any
from abc import ABC, abstractmethod
from tools.database_singleton import database_singleton

class BaseAgent(ABC):
    """Interfaz común para todos los agentes"""
    
    @abstractmethod
    def run(self, user_input: str, database_schema: Dict[str, Any] = None, relevant_schema_content: str = None) -> str:
        """Método estándar que todos los agentes deben implementar"""
        pass

# Registro global de agentes con lazy loading
AGENT_REGISTRY: Dict[str, Type[BaseAgent]] = {}
AGENT_INSTANCES: Dict[str, BaseAgent] = {}

def register_agent(name: str):
    """Decorador para registrar agentes automáticamente"""
    def decorator(cls: Type[BaseAgent]) -> Type[BaseAgent]:
        if not issubclass(cls, BaseAgent):
            raise ValueError(f"Agente {name} debe heredar de BaseAgent")
        AGENT_REGISTRY[name] = cls
        return cls
    return decorator

def get_agent(name: str) -> BaseAgent:
    """Obtener una instancia de un agente por nombre (lazy loading)"""
    if name not in AGENT_REGISTRY:
        raise ValueError(f"Agente '{name}' no encontrado en el registro")
    
    # Lazy loading: crear instancia solo cuando se necesita
    if name not in AGENT_INSTANCES:
        print(f"🔄 Creando instancia de agente: {name}")
        AGENT_INSTANCES[name] = AGENT_REGISTRY[name]()
        print(f"✅ Agente {name} inicializado")
    
    return AGENT_INSTANCES[name]

def list_available_agents() -> list:
    """Listar todos los agentes disponibles"""
    return list(AGENT_REGISTRY.keys())

def agent_exists(name: str) -> bool:
    """Verificar si un agente existe en el registro"""
    return name in AGENT_REGISTRY

def preload_agent(name: str) -> BaseAgent:
    """Pre-cargar un agente específico (útil para agentes críticos)"""
    return get_agent(name)

def get_loaded_agents() -> list:
    """Obtener lista de agentes ya cargados en memoria"""
    return list(AGENT_INSTANCES.keys()) 