# Importar el registro optimizado
from . import registry

# Importar solo las clases de agentes para registro (no crear instancias)
from .sales_agent.agent import SalesAgent
from .finance_agent.agent import FinanceAgent
from .inventory_agent.agent import InventoryAgent
from .field_ops_agent.agent import FieldOpsAgent
from .strategy_agent.agent import StrategyAgent
from .client_agent.agent import ClientAgent

# Exportar el registro y funciones útiles
from .registry import (
    AGENT_REGISTRY,
    AGENT_INSTANCES,
    get_agent,
    list_available_agents,
    agent_exists,
    preload_agent,
    get_loaded_agents,
    BaseAgent,
    register_agent
)

__all__ = [
    'AGENT_REGISTRY',
    'AGENT_INSTANCES',
    'get_agent', 
    'list_available_agents',
    'agent_exists',
    'preload_agent',
    'get_loaded_agents',
    'BaseAgent',
    'register_agent'
] 