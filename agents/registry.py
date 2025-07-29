# Importar desde el registro optimizado
from .optimized_registry import (
    BaseAgent,
    AGENT_REGISTRY,
    AGENT_INSTANCES,
    register_agent,
    get_agent,
    list_available_agents,
    agent_exists,
    preload_agent,
    get_loaded_agents
)

# Re-exportar para compatibilidad
__all__ = [
    'BaseAgent',
    'AGENT_REGISTRY',
    'AGENT_INSTANCES',
    'register_agent',
    'get_agent',
    'list_available_agents',
    'agent_exists',
    'preload_agent',
    'get_loaded_agents'
] 