from langchain_core.tools import tool
from db.database_manager import db_manager
from typing import Optional
import logging

logger = logging.getLogger(__name__)

@tool
def query_database(query: str, db_type: str = "sqlserver") -> str:
    """
    Ejecuta una consulta SQL en la base de datos especificada
    
    Args:
        query: Consulta SQL a ejecutar
        db_type: Tipo de base de datos ("sqlserver", "postgres", "mysql")
    
    Returns:
        Resultado de la consulta en formato JSON
    """
    try:
        results = db_manager.execute_query(query, db_type)
        return f"Query executed successfully. Results: {results}"
    except Exception as e:
        logger.error(f"Database query error: {e}")
        return f"Error executing query: {str(e)}"
