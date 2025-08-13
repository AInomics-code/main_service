from langchain_core.tools import tool
from tools.simple_db_tool import create_database_tool
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Create the database tool instance once using the working implementation from master
_db_tool = create_database_tool(settings.SQLSERVER_URL)

@tool
def query_database(query: str, db_type: str = "sqlserver") -> str:
    """
    Ejecuta una consulta SQL en la base de datos especificada usando la implementación funcional de simple_db_tool
    
    Args:
        query: Consulta SQL a ejecutar
        db_type: Tipo de base de datos ("sqlserver", "postgres", "mysql")
    
    Returns:
        Resultado de la consulta en formato JSON
    """
    print(f"\n🗄️ QUERY_DATABASE TOOL CALLED")
    print(f"   Database: {db_type}")
    print(f"   📊 SQL Query:")
    print(f"   {query}")
    print(f"   " + "="*50)
    
    try:
        # Use the simple_db_tool implementation that works correctly
        result = _db_tool._run(query)
        
        print(f"   ✅ Query executed successfully")
        print(f"   📈 Result preview: {result[:200]}...")
        
        return result
    except Exception as e:
        print(f"   ❌ Database query error: {e}")
        logger.error(f"Database query error: {e}")
        return f"Error executing query: {str(e)}"
