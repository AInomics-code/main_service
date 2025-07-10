# Importar todos los agentes para que se registren automáticamente
from . import registry

# Importar solo los agentes que están en el catálogo del pipeline_planner
from .kpi_fetcher.agent import KPIFetcherAgent
from .comparator.agent import ComparatorAgent
from .ranker.agent import RankerAgent
from .time_series_loader.agent import TimeSeriesLoaderAgent
from .trend_detector.agent import TrendDetectorAgent
from .forecast_agent.agent import ForecastAgent
from .pattern_finder.agent import PatternFinderAgent
from .root_cause_analyst.agent import RootCauseAnalystAgent
from .cost_margin_fetcher.agent import CostMarginFetcherAgent
from .budget_variance_agent.agent import BudgetVarianceAgent
from .inventory_checker.agent import InventoryCheckerAgent
from .bo_checker.agent import BOCheckerAgent
from .client_list_loader.agent import ClientListLoaderAgent
from .coverage_analyzer.agent import CoverageAnalyzerAgent
from .route_loader.agent import RouteLoaderAgent
from .attendance_checker.agent import AttendanceCheckerAgent
from .ar_aging_agent.agent import ARAgingAgent
from .lookup.agent import LookupAgent
from .fallback_llm.agent import FallbackLLMAgent
from .strategist.agent import StrategistAgent

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