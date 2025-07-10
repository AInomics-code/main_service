from typing import Dict, Type, Any
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Interfaz común para todos los agentes"""
    
    @abstractmethod
    def run(self, user_input: str) -> str:
        """Método estándar que todos los agentes deben implementar"""
        pass

# Registro global de agentes
AGENT_REGISTRY: Dict[str, Type[BaseAgent]] = {}

def register_agent(name: str):
    """Decorador para registrar agentes automáticamente"""
    def decorator(cls: Type[BaseAgent]) -> Type[BaseAgent]:
        if not issubclass(cls, BaseAgent):
            raise ValueError(f"Agente {name} debe heredar de BaseAgent")
        AGENT_REGISTRY[name] = cls
        return cls
    return decorator

def get_agent(name: str) -> BaseAgent:
    """Obtener una instancia de un agente por nombre"""
    if name not in AGENT_REGISTRY:
        raise ValueError(f"Agente '{name}' no encontrado en el registro")
    return AGENT_REGISTRY[name]()

def list_available_agents() -> list:
    """Listar todos los agentes disponibles"""
    return list(AGENT_REGISTRY.keys())

def agent_exists(name: str) -> bool:
    """Verificar si un agente existe en el registro"""
    return name in AGENT_REGISTRY 