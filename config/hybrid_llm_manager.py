from langchain_openai import ChatOpenAI
from typing import Dict, Any
from config.settings import settings
from config.hybrid_llm_config import HYBRID_LLM_CONFIG

class HybridLLMManager:
    """
    Manager híbrido para manejar LLMs compartidos y especializados
    """
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HybridLLMManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.shared_llm = None
        self.specialized_llms = {}
        self.config = HYBRID_LLM_CONFIG
    
    def get_llm_for_agent(self, agent_name: str) -> ChatOpenAI:
        """
        Obtiene el LLM apropiado para un agente específico
        """
        # Si el agente usa LLM compartido
        if agent_name in self.config["shared_llm"]["agents"]:
            return self._get_shared_llm()
        
        # Si el agente usa LLM especializado
        if agent_name in self.config["specialized_llms"]:
            return self._get_specialized_llm(agent_name)
        
        # Fallback al LLM compartido
        return self._get_shared_llm()
    
    def _get_shared_llm(self) -> ChatOpenAI:
        """Obtiene o crea el LLM compartido"""
        if self.shared_llm is None:
            config = self.config["shared_llm"].copy()
            config["openai_api_key"] = settings.OPENAI_KEY
            # Remover campos que no son válidos para ChatOpenAI
            config.pop("agents", None)
            self.shared_llm = ChatOpenAI(**config)
        return self.shared_llm
    
    def _get_specialized_llm(self, agent_name: str) -> ChatOpenAI:
        """Obtiene o crea un LLM especializado"""
        if agent_name not in self.specialized_llms:
            config = self.config["specialized_llms"][agent_name].copy()
            config["openai_api_key"] = settings.OPENAI_KEY
            # Remover campos que no son válidos para ChatOpenAI
            config.pop("agents", None)
            self.specialized_llms[agent_name] = ChatOpenAI(**config)
        return self.specialized_llms[agent_name]
    
    def preload_critical_agents(self):
        """Pre-carga agentes críticos al startup"""
        critical_agents = ["StrategyAgent", "LanguageDetector", "Supervisor"]
        for agent in critical_agents:
            self.get_llm_for_agent(agent)
    
    def get_loaded_agents(self) -> Dict[str, str]:
        """Retorna información sobre agentes cargados"""
        loaded = {}
        
        if self.shared_llm:
            loaded["shared"] = f"Modelo: {self.shared_llm.model_name}"
        
        for agent_name, llm in self.specialized_llms.items():
            loaded[agent_name] = f"Modelo: {llm.model_name}, Temp: {llm.temperature}"
        
        return loaded

# Instancia global del manager
hybrid_llm_manager = HybridLLMManager() 