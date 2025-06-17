from langchain.utilities import SQLDatabase
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
import os
import json
from typing import Optional, Dict, List, Any
from langchain.base_language import BaseLanguageModel
from sqlalchemy import text

from config.settings import settings
from config.redis_config import get_redis_client

class DatabaseTool:
    def __init__(self, db_url: Optional[str] = None, llm: Optional[BaseLanguageModel] = None):
        """
        Initialize the database tool with a connection URL or use environment variables
        
        Args:
            db_url (str, optional): Database connection URL. If not provided, will use environment variables
            llm (BaseLanguageModel, optional): Language model to use for the toolkit
        """
        self.db_url = db_url or settings.PG_URL
        if not self.db_url:
            raise ValueError("Database URL must be provided either as parameter or DATABASE_URL environment variable")
        
        self.db = SQLDatabase.from_uri(self.db_url)
        self.llm = llm
    
    def get_tools(self):
        """
        Get the SQL database tools
        
        Returns:
            list: List of SQL database tools
        """
        if not self.llm:
            raise ValueError("Language model (llm) must be provided before getting tools")
        return SQLDatabaseToolkit(db=self.db, llm=self.llm).get_tools()
    
    def get_db(self):
        """
        Get the database connection
        
        Returns:
            SQLDatabase: Database connection instance
        """
        return self.db
    
    def get_schema_json(self) -> Dict[str, Any]:
        """
        Get the complete database schema in JSON format
        
        Returns:
            Dict[str, Any]: Dictionary containing all tables and their attributes
        """
        try:
            engine = self.db._engine
            
            # Query to get all tables and their columns with detailed information
            query = """
            SELECT 
                t.table_name,
                c.column_name,
                c.data_type,
                c.is_nullable,
                c.column_default,
                c.character_maximum_length,
                c.numeric_precision,
                c.numeric_scale,
                c.ordinal_position,
                CASE 
                    WHEN pk.column_name IS NOT NULL THEN true 
                    ELSE false 
                END as is_primary_key,
                CASE 
                    WHEN fk.column_name IS NOT NULL THEN true 
                    ELSE false 
                END as is_foreign_key,
                fk.foreign_table_name,
                fk.foreign_column_name
            FROM 
                information_schema.tables t
            LEFT JOIN 
                information_schema.columns c ON t.table_name = c.table_name
            LEFT JOIN (
                SELECT 
                    ku.table_name,
                    ku.column_name
                FROM 
                    information_schema.table_constraints tc
                JOIN 
                    information_schema.key_column_usage ku 
                    ON tc.constraint_name = ku.constraint_name
                WHERE 
                    tc.constraint_type = 'PRIMARY KEY'
            ) pk ON c.table_name = pk.table_name AND c.column_name = pk.column_name
            LEFT JOIN (
                SELECT 
                    ku.table_name,
                    ku.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM 
                    information_schema.table_constraints tc
                JOIN 
                    information_schema.key_column_usage ku 
                    ON tc.constraint_name = ku.constraint_name
                JOIN 
                    information_schema.constraint_column_usage ccu 
                    ON tc.constraint_name = ccu.constraint_name
                WHERE 
                    tc.constraint_type = 'FOREIGN KEY'
            ) fk ON c.table_name = fk.table_name AND c.column_name = fk.column_name
            WHERE 
                t.table_schema = 'public' 
                AND t.table_type = 'BASE TABLE'
            ORDER BY 
                t.table_name, c.ordinal_position;
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
                        "columns": []
                    }
                
                # Build column information
                column_info = {
                    "column_name": row[1],
                    "data_type": row[2],
                    "is_nullable": row[3] == "YES"
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
            raise Exception(f"Error extracting database schema: {str(e)}")
    
    def get_cached_schema_json(self) -> Dict[str, Any]:
        """
        Get the database schema from Redis cache or generate and cache it
        
        Returns:
            Dict[str, Any]: Dictionary containing all tables and their attributes
        """
        redis_client = get_redis_client()
        cache_key = f"db_schema:{self.db_url.split('/')[-1] if '/' in self.db_url else 'default'}"
        
        try:
            # Try to get from cache first
            cached_schema = redis_client.get(cache_key)
            
            if cached_schema:
                print(f"Using cached schema from Redis")
                return json.loads(cached_schema)
            
            # If not in cache, generate the schema
            print(f"No cached schema found in Redis. Generating new schema.")
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
            print(f"Redis cache error: {str(e)}. Falling back to direct schema generation.")
            return self.get_schema_json()
    
 