from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
import os
import json
from typing import Optional, Dict, List, Any
from langchain.base_language import BaseLanguageModel
from sqlalchemy import text

from config.settings import settings
from config.redis_config import get_redis_client

class SQLServerDatabaseTool:
    def __init__(self, db_url: Optional[str] = None, llm: Optional[BaseLanguageModel] = None):
        """
        Initialize the SQL Server database tool with a connection URL or use environment variables
        
        Args:
            db_url (str, optional): SQL Server database connection URL. If not provided, will use SQLSERVER_URL environment variable
            llm (BaseLanguageModel, optional): Language model to use for the toolkit
        """
        self.db_url = db_url or settings.SQLSERVER_URL
        if not self.db_url:
            raise ValueError("SQL Server database URL must be provided either as parameter or SQLSERVER_URL environment variable")
        
        # Ensure the URL uses the correct SQL Server format
        if not self.db_url.startswith('mssql'):
            if self.db_url.startswith('sqlserver://'):
                self.db_url = self.db_url.replace('sqlserver://', 'mssql+pyodbc://', 1)
            elif not self.db_url.startswith('mssql+pyodbc://'):
                self.db_url = f"mssql+pyodbc://{self.db_url}"
        
        self.db = SQLDatabase.from_uri(self.db_url)
        self.llm = llm
        
        # Create the actual toolkit
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        
        # Set dialect for compatibility with create_sql_agent
        self.dialect = "mssql"
    
    def get_tools(self):
        """
        Get the SQL database tools for SQL Server
        
        Returns:
            list: List of SQL database tools
        """
        if not self.llm:
            raise ValueError("Language model (llm) must be provided before getting tools")
        return self.toolkit.get_tools()
    
    def get_db(self):
        """
        Get the SQL Server database connection
        
        Returns:
            SQLDatabase: Database connection instance
        """
        return self.db
    
    def get_schema_json(self) -> Dict[str, Any]:
        """
        Get the complete SQL Server database schema in JSON format
        
        Returns:
            Dict[str, Any]: Dictionary containing all tables and their attributes
        """
        try:
            engine = self.db._engine
            
            # Simplified SQL Server query to get basic table and column information
            query = """
            SELECT 
                t.name AS table_name,
                c.name AS column_name,
                ty.name AS data_type
            FROM 
                sys.tables t
            LEFT JOIN 
                sys.columns c ON t.object_id = c.object_id
            LEFT JOIN 
                sys.types ty ON c.user_type_id = ty.user_type_id
            WHERE 
                t.type = 'U'  -- User tables only
            ORDER BY 
                t.name, c.column_id;
            """
            
            # Execute the query using the new SQLAlchemy 2.0+ API
            with engine.connect() as connection:
                result = connection.execute(text(query))
                rows = result.fetchall()
            
            # Organize the data by table
            schema = {}
            
            for row in rows:
                table_name = row[0]
                if table_name not in schema:
                    schema[table_name] = {
                        "table_name": table_name,
                        "description": "",
                        "columns": []
                    }
                
                # Build column information with only basic fields
                column_info = {
                    "column_name": row[1],
                    "data_type": row[2],
                    "description": ""
                }
                
                schema[table_name]["columns"].append(column_info)
            
            # Create final structure
            database_schema = {
                "database_name": self.db_url.split("/")[-1] if "/" in self.db_url else "unknown",
                "tables": list(schema.values()),
                "table_count": len(schema),
                "total_columns": sum(len(table["columns"]) for table in schema.values())
            }
            
            return database_schema
            
        except Exception as e:
            raise Exception(f"Error extracting SQL Server database schema: {str(e)}")
    
    def get_cached_schema_json(self) -> Dict[str, Any]:
        """
        Get the SQL Server database schema from Redis cache or generate and cache it
        
        Returns:
            Dict[str, Any]: Dictionary containing all tables and their attributes
        """
        redis_client = get_redis_client()
        cache_key = f"sqlserver_schema:{self.db_url.split('/')[-1] if '/' in self.db_url else 'default'}"
        
        try:
            # Try to get from cache first
            cached_schema = redis_client.get(cache_key)
            
            if cached_schema:
                print(f"Using cached SQL Server schema from Redis")
                return json.loads(cached_schema)
            
            # If not in cache, generate the schema
            print(f"No cached SQL Server schema found in Redis. Generating new schema.")
            schema = self.get_schema_json()
            
            # Cache the result with 24 hours TTL (86400 seconds)
            redis_client.setex(
                cache_key, 
                86400,  # 24 hours in seconds
                json.dumps(schema, default=str)
            )
            
            return schema
            
        except Exception as e:
            # If Redis fails, fallback to direct schema generation
            print(f"Redis cache error: {str(e)}. Falling back to direct SQL Server schema generation.")
            return self.get_schema_json() 