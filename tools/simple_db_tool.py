import pyodbc
import pymysql
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict
import json
import time

class DatabaseQueryInput(BaseModel):
    query: str = Field(description="SQL query to execute")

class SimpleDatabaseTool(BaseTool):
    name: str = "simple_database_query"
    description: str = "Execute SQL queries on any database (SQL Server, MySQL, PostgreSQL)"
    args_schema: type[BaseModel] = DatabaseQueryInput
    
    # Permitir campos extra para evitar errores de Pydantic
    model_config = ConfigDict(extra="allow")
    
    def __init__(self, default_connection_string: str = None):
        super().__init__()
        self.default_connection_string = default_connection_string
        self._engine_cache = {}
    
    def _get_engine(self, connection_string: str):
        """Get or create SQLAlchemy engine for connection string"""
        if connection_string not in self._engine_cache:
            try:
                self._engine_cache[connection_string] = create_engine(connection_string)
            except Exception as e:
                raise ValueError(f"Invalid connection string: {str(e)}")
        return self._engine_cache[connection_string]
    
    def _execute_query(self, query: str, connection_string: str) -> Dict[str, Any]:
        """Execute SQL query and return results"""
        start_time = time.time()
        
        try:
            engine = self._get_engine(connection_string)
            
            with engine.connect() as connection:
                result = connection.execute(text(query))
                
                # Get column names
                columns = list(result.keys())
                
                # Fetch all rows
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
                
                execution_time = time.time() - start_time
                
                return {
                    "success": True,
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows),
                    "execution_time": f"{execution_time:.3f}s",
                    "query": query
                }
                
        except SQLAlchemyError as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "execution_time": f"{execution_time:.3f}s",
                "query": query
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "execution_time": f"{execution_time:.3f}s",
                "query": query
            }
    
    def _run(self, query: str) -> str:
        """Execute the database query"""
        if not self.default_connection_string:
            return "Error: No connection string configured"
        
        result = self._execute_query(query, self.default_connection_string)
        
        if result["success"]:
            # Format successful result
            response = f"Query executed successfully in {result['execution_time']}\n"
            response += f"Rows returned: {result['row_count']}\n\n"
            
            if result['rows']:
                # Show first few rows as example
                sample_rows = result['rows'][:5]
                response += "Sample results:\n"
                for i, row in enumerate(sample_rows, 1):
                    response += f"Row {i}: {json.dumps(row, default=str)}\n"
                
                if len(result['rows']) > 5:
                    response += f"\n... and {len(result['rows']) - 5} more rows"
            else:
                response += "No rows returned"
        else:
            # Format error result
            response = f"Query failed after {result['execution_time']}\n"
            response += f"Error: {result['error']}"
        
        return response
    
    def get_schema_info(self) -> str:
        """Get database schema information"""
        if not self.default_connection_string:
            return "Error: No connection string configured"
        
        connection_string = self.default_connection_string
        
        try:
            engine = self._get_engine(connection_string)
            
            # Detect database type
            if "sqlserver" in connection_string.lower() or "mssql" in connection_string.lower():
                return self._get_sqlserver_schema(engine)
            elif "mysql" in connection_string.lower():
                return self._get_mysql_schema(engine)
            elif "postgresql" in connection_string.lower() or "postgres" in connection_string.lower():
                return self._get_postgresql_schema(engine)
            else:
                return "Database type not recognized"
                
        except Exception as e:
            return f"Error getting schema: {str(e)}"
    
    def _get_sqlserver_schema(self, engine) -> str:
        """Get SQL Server schema"""
        query = """
        SELECT 
            t.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.character_maximum_length
        FROM information_schema.tables t
        JOIN information_schema.columns c ON t.table_name = c.table_name
        WHERE t.table_type = 'BASE TABLE'
        ORDER BY t.table_name, c.ordinal_position
        """
        
        result = self._execute_query(query, str(engine.url))
        if result["success"]:
            return self._format_schema_result(result["rows"])
        return f"Error: {result['error']}"
    
    def _get_mysql_schema(self, engine) -> str:
        """Get MySQL schema"""
        query = """
        SELECT 
            TABLE_NAME as table_name,
            COLUMN_NAME as column_name,
            DATA_TYPE as data_type,
            IS_NULLABLE as is_nullable,
            CHARACTER_MAXIMUM_LENGTH as character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
        ORDER BY table_name, ordinal_position
        """
        
        result = self._execute_query(query, str(engine.url))
        if result["success"]:
            return self._format_schema_result(result["rows"])
        return f"Error: {result['error']}"
    
    def _get_postgresql_schema(self, engine) -> str:
        """Get PostgreSQL schema"""
        query = """
        SELECT 
            t.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.character_maximum_length
        FROM information_schema.tables t
        JOIN information_schema.columns c ON t.table_name = c.table_name
        WHERE t.table_schema = 'public' AND t.table_type = 'BASE TABLE'
        ORDER BY t.table_name, c.ordinal_position
        """
        
        result = self._execute_query(query, str(engine.url))
        if result["success"]:
            return self._format_schema_result(result["rows"])
        return f"Error: {result['error']}"
    
    def _format_schema_result(self, rows: List[Dict]) -> str:
        """Format schema information"""
        if not rows:
            return "No tables found"
        
        current_table = None
        schema_info = "Database Schema:\n\n"
        
        for row in rows:
            table_name = row['table_name']
            column_name = row['column_name']
            data_type = row['data_type']
            is_nullable = row['is_nullable']
            
            if table_name != current_table:
                if current_table:
                    schema_info += "\n"
                current_table = table_name
                schema_info += f"Table: {table_name}\n"
                schema_info += "-" * (len(table_name) + 7) + "\n"
            
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            schema_info += f"  {column_name}: {data_type} ({nullable})\n"
        
        return schema_info

# Tool factory for easy creation
def create_database_tool(connection_string: str) -> SimpleDatabaseTool:
    """Create a database tool with a specific connection string"""
    return SimpleDatabaseTool(default_connection_string=connection_string) 