from typing import Dict, Any

# Configuración híbrida de LLMs
HYBRID_LLM_CONFIG = {
    "shared_llm": {
        "model": "gpt-4o-mini",
        "temperature": 0,
        "max_tokens": 1000,
        "openai_api_key": None,  # Se inyecta desde settings
        "agents": [
            "SalesAgent", 
            "FinanceAgent", 
            "InventoryAgent", 
            "FieldOpsAgent", 
            "ClientAgent"
        ]
    },
    "specialized_llms": {
        "StrategyAgent": {
            "model": "gpt-4o-mini",
            "temperature": 0.1,  # Más creativo para estrategia
            "max_tokens": 2000,  # Respuestas más largas
            "openai_api_key": None
        },
        "LanguageDetector": {
            "model": "gpt-3.5-turbo",  # Más rápido y barato
            "temperature": 0,
            "max_tokens": 50,
            "openai_api_key": None
        },
        "Supervisor": {
            "model": "gpt-4o-mini",
            "temperature": 0.05,  # Muy preciso para síntesis
            "max_tokens": 3000,
            "openai_api_key": None
        },
        "PipelinePlanner": {
            "model": "gpt-4o-mini",
            "temperature": 0,
            "max_tokens": 500,
            "openai_api_key": None
        }
    }
}

# Configuración de agentes para el pipeline
AGENT_CONFIG = {
    "SalesAgent": {
        "max_iterations": 3,
        "max_execution_time": 30,
        "early_stopping_method": "force"
    },
    "FinanceAgent": {
        "max_iterations": 3,
        "max_execution_time": 30,
        "early_stopping_method": "force"
    },
    "InventoryAgent": {
        "max_iterations": 3,
        "max_execution_time": 30,
        "early_stopping_method": "force"
    },
    "FieldOpsAgent": {
        "max_iterations": 3,
        "max_execution_time": 30,
        "early_stopping_method": "force"
    },
    "ClientAgent": {
        "max_iterations": 3,
        "max_execution_time": 30,
        "early_stopping_method": "force"
    },
    "StrategyAgent": {
        "max_iterations": 3,
        "max_execution_time": 30,
        "early_stopping_method": "force"
    },
    "Supervisor": {
        "max_iterations": 6,
        "max_execution_time": 60,
        "early_stopping_method": "generate"
    }
} 