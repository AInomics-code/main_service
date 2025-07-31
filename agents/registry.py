from typing import Dict, Type, Optional
from .base_agent import BaseAgent

# Registro de agentes
AGENT_REGISTRY: Dict[str, Type[BaseAgent]] = {}
AGENT_INSTANCES: Dict[str, BaseAgent] = {}

def register_agent(name: str):
    """Decorador para registrar un agente"""
    def decorator(agent_class: Type[BaseAgent]):
        AGENT_REGISTRY[name] = agent_class
        return agent_class
    return decorator

def get_agent(name: str) -> Optional[BaseAgent]:
    """Obtener una instancia de agente (lazy loading)"""
    if name not in AGENT_INSTANCES:
        if name in AGENT_REGISTRY:
            AGENT_INSTANCES[name] = AGENT_REGISTRY[name]()
        else:
            return None
    return AGENT_INSTANCES[name]

def list_available_agents() -> list:
    """Listar todos los agentes disponibles"""
    return list(AGENT_REGISTRY.keys())

def agent_exists(name: str) -> bool:
    """Verificar si un agente existe"""
    return name in AGENT_REGISTRY

def preload_agent(name: str) -> bool:
    """Pre-cargar un agente específico"""
    if agent_exists(name):
        get_agent(name)  # Esto creará la instancia
        return True
    return False

def get_loaded_agents() -> list:
    """Obtener lista de agentes ya cargados"""
    return list(AGENT_INSTANCES.keys()) 