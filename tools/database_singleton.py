from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from langchain.base_language import BaseLanguageModel
from typing import Optional, Dict, List, Any
from config.settings import settings
from .sqlserver_database_tool import SQLServerDatabaseTool

class DatabaseToolSingleton:
    """
    Singleton para herramientas de base de datos para evitar múltiples conexiones costosas.
    """
    _instance = None
    _initialized = False
    _db_tool = None
    _llm = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseToolSingleton, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._db_tool = None
        self._llm = None
    
    def get_llm(self) -> ChatOpenAI:
        """Obtiene o crea la instancia del LLM (Singleton)"""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model="gpt-4o-mini",  # Cambia a GPT-4o-mini (mejor seguimiento de instrucciones)
                temperature=0,
                openai_api_key=settings.OPENAI_KEY,
                model_kwargs={
                    "stop": ["Observation:"],  # Para ayudar a parar después de obtener resultados
                }
            )
        return self._llm
    
    def get_database_tool(self) -> SQLServerDatabaseTool:
        """Obtiene o crea la herramienta de base de datos (Singleton)"""
        if self._db_tool is None:
            self._db_tool = SQLServerDatabaseTool(llm=self.get_llm())
        return self._db_tool
    
    def get_tools(self):
        """Obtiene las herramientas de base de datos"""
        return self.get_database_tool().get_tools()

# Instancia global
database_singleton = DatabaseToolSingleton() 