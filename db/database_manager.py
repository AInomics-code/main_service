import pyodbc
import psycopg2
import pymysql
from contextlib import contextmanager
from typing import Optional, Dict, Any
import threading
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor de conexiones de base de datos compartidas para optimizar el tiempo de carga"""
    
    def __init__(self):
        self._connections = {}
        self._lock = threading.Lock()
        self._connection_pools = {}
    
    def _get_sqlserver_connection(self) -> pyodbc.Connection:
        """Obtiene una conexión a SQL Server"""
        try:
            connection = pyodbc.connect(settings.SQLSERVER_URL)
            return connection
        except Exception as e:
            logger.error(f"Error connecting to SQL Server: {e}")
            raise
    
    def _get_postgres_connection(self) -> psycopg2.extensions.connection:
        """Obtiene una conexión a PostgreSQL"""
        try:
            connection = psycopg2.connect(settings.PG_URL)
            return connection
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL: {e}")
            raise
    
    def _get_mysql_connection(self) -> pymysql.Connection:
        """Obtiene una conexión a MySQL"""
        try:
            connection = pymysql.connect(settings.MYSQL_URL)
            return connection
        except Exception as e:
            logger.error(f"Error connecting to MySQL: {e}")
            raise
    
    @contextmanager
    def get_connection(self, db_type: str = "sqlserver"):
        """
        Context manager para obtener una conexión de base de datos
        
        Args:
            db_type: Tipo de base de datos ("sqlserver", "postgres", "mysql")
        
        Yields:
            Conexión de base de datos
        """
        connection = None
        try:
            if db_type == "sqlserver":
                connection = self._get_sqlserver_connection()
            elif db_type == "postgres":
                connection = self._get_postgres_connection()
            elif db_type == "mysql":
                connection = self._get_mysql_connection()
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            yield connection
            
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection:
                try:
                    connection.close()
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
    
    def execute_query(self, query: str, db_type: str = "sqlserver", params: Optional[tuple] = None) -> list:
        """
        Ejecuta una consulta SQL y retorna los resultados
        
        Args:
            query: Consulta SQL a ejecutar
            db_type: Tipo de base de datos
            params: Parámetros para la consulta (opcional)
        
        Returns:
            Lista de resultados
        """
        with self.get_connection(db_type) as connection:
            cursor = connection.cursor()
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().upper().startswith('SELECT'):
                    columns = [column[0] for column in cursor.description]
                    results = []
                    for row in cursor.fetchall():
                        results.append(dict(zip(columns, row)))
                    return results
                else:
                    connection.commit()
                    return [{"affected_rows": cursor.rowcount}]
                    
            except Exception as e:
                logger.error(f"Query execution error: {e}")
                connection.rollback()
                raise
            finally:
                cursor.close()
    
    def execute_many(self, query: str, params_list: list, db_type: str = "sqlserver") -> dict:
        """
        Ejecuta múltiples consultas con diferentes parámetros
        
        Args:
            query: Consulta SQL base
            params_list: Lista de parámetros para cada ejecución
            db_type: Tipo de base de datos
        
        Returns:
            Resultado de la ejecución
        """
        with self.get_connection(db_type) as connection:
            cursor = connection.cursor()
            try:
                cursor.executemany(query, params_list)
                connection.commit()
                return {"affected_rows": cursor.rowcount}
            except Exception as e:
                logger.error(f"Batch execution error: {e}")
                connection.rollback()
                raise
            finally:
                cursor.close()
    
    def test_connection(self, db_type: str = "sqlserver") -> bool:
        """
        Prueba la conexión a la base de datos
        
        Args:
            db_type: Tipo de base de datos
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        try:
            with self.get_connection(db_type) as connection:
                cursor = connection.cursor()
                if db_type == "sqlserver":
                    cursor.execute("SELECT 1")
                elif db_type == "postgres":
                    cursor.execute("SELECT 1")
                elif db_type == "mysql":
                    cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                return True
        except Exception as e:
            logger.error(f"Connection test failed for {db_type}: {e}")
            return False

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()
