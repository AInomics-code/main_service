# Importar todos los agentes para que se registren automáticamente
from . import registry

# Importar solo los agentes que están en el catálogo del pipeline_planner
from .sales_agent.agent import SalesAgent
from .finance_agent.agent import FinanceAgent
from .inventory_agent.agent import InventoryAgent
from .field_ops_agent.agent import FieldOpsAgent
from .strategy_agent.agent import StrategyAgent
from .client_agent.agent import ClientAgent

# Exportar el registro y funciones útiles
from .registry import (
    AGENT_REGISTRY,
    get_agent,
    list_available_agents,
    agent_exists,
    BaseAgent,
    register_agent
)

__all__ = [
    'AGENT_REGISTRY',
    'get_agent', 
    'list_available_agents',
    'agent_exists',
    'BaseAgent',
    'register_agent'
] 