from typing import List, Dict, Any, Optional
from langchain.tools import BaseTool
from tools.simple_db_tool import create_database_tool
from config.settings import settings
from pydantic import ConfigDict

class ToolManager:
    """
    Manager para manejar múltiples herramientas de forma escalable
    """
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._tools_cache = {}
        self._default_tools = []
        self._setup_default_tools()
    
    def _setup_default_tools(self):
        """Configurar herramientas por defecto"""
        # Crear herramienta de base de datos con SQL Server
        db_tool = create_database_tool(settings.SQLSERVER_URL)
        self._default_tools.append(db_tool)
        
        # Agregar herramienta de schema
        schema_tool = self._create_schema_tool()
        self._default_tools.append(schema_tool)
    
    def _create_schema_tool(self) -> BaseTool:
        """Crear herramienta para obtener información del schema"""
        from langchain.tools import BaseTool
        from pydantic import BaseModel, Field
        
        class SchemaInput(BaseModel):
            table_name: str = Field(description="Table name to get schema info for", default="")
        
        class SchemaTool(BaseTool):
            name: str = "get_database_schema"
            description: str = "Get database schema information for tables"
            args_schema: type[BaseModel] = SchemaInput
            
            # Permitir campos extra para evitar errores de Pydantic
            model_config = ConfigDict(extra="allow")
            
            def __init__(self, db_tool):
                super().__init__()
                self.db_tool = db_tool
            
            def _run(self, table_name: str = "") -> str:
                if table_name:
                    # Get specific table schema
                    query = f"""
                    SELECT 
                        c.column_name,
                        c.data_type,
                        c.is_nullable,
                        c.character_maximum_length
                    FROM information_schema.columns c
                    WHERE c.table_name = '{table_name}'
                    ORDER BY c.ordinal_position
                    """
                    return self.db_tool._run(query)
                else:
                    # Get all tables schema
                    return self.db_tool.get_schema_info()
        
        return SchemaTool(self._default_tools[0])  # db_tool
    
    def get_default_tools(self) -> List[BaseTool]:
        """Obtener herramientas por defecto"""
        return self._default_tools.copy()
    
    def add_tool(self, tool: BaseTool, tool_name: str = None):
        """Agregar una nueva herramienta"""
        if tool_name is None:
            tool_name = tool.name
        
        self._tools_cache[tool_name] = tool
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Obtener una herramienta específica"""
        return self._tools_cache.get(tool_name)
    
    def get_all_tools(self) -> List[BaseTool]:
        """Obtener todas las herramientas (default + custom)"""
        all_tools = self._default_tools.copy()
        all_tools.extend(self._tools_cache.values())
        return all_tools
    
    def create_database_tool(self, connection_string: str, tool_name: str = None) -> BaseTool:
        """Crear una nueva herramienta de base de datos"""
        db_tool = create_database_tool(connection_string)
        
        if tool_name:
            db_tool.name = tool_name
        
        self.add_tool(db_tool, tool_name)
        return db_tool
    
    def remove_tool(self, tool_name: str) -> bool:
        """Remover una herramienta"""
        if tool_name in self._tools_cache:
            del self._tools_cache[tool_name]
            return True
        return False
    
    def list_tools(self) -> Dict[str, str]:
        """Listar todas las herramientas disponibles"""
        tools_info = {}
        
        # Default tools
        for tool in self._default_tools:
            tools_info[tool.name] = f"Default: {tool.description}"
        
        # Custom tools
        for name, tool in self._tools_cache.items():
            tools_info[name] = f"Custom: {tool.description}"
        
        return tools_info

# Instancia global del manager
tool_manager = ToolManager() 