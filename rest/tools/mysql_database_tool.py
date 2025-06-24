from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
import os
import json
from typing import Optional, Dict, List, Any
from langchain.base_language import BaseLanguageModel
from sqlalchemy import text

from config.settings import settings
from config.redis_config import get_redis_client

class MySQLDatabaseTool:
    def __init__(self, db_url: Optional[str] = None, llm: Optional[BaseLanguageModel] = None):
        """
        Initialize the MySQL database tool with a connection URL or use environment variables
        
        Args:
            db_url (str, optional): MySQL database connection URL. If not provided, will use MYSQL_URL environment variable
            llm (BaseLanguageModel, optional): Language model to use for the toolkit
        """
        self.db_url = db_url or settings.MYSQL_URL
        if not self.db_url:
            raise ValueError("MySQL database URL must be provided either as parameter or MYSQL_URL environment variable")
        
        # Ensure the URL uses the correct MySQL format
        if not self.db_url.startswith('mysql'):
            if self.db_url.startswith('mysql://'):
                self.db_url = self.db_url.replace('mysql://', 'mysql+pymysql://', 1)
            else:
                self.db_url = f"mysql+pymysql://{self.db_url}"
        
        self.db = SQLDatabase.from_uri(self.db_url)
        self.llm = llm
    
    def get_tools(self):
        """
        Get the SQL database tools for MySQL
        
        Returns:
            list: List of SQL database tools
        """
        if not self.llm:
            raise ValueError("Language model (llm) must be provided before getting tools")
        return SQLDatabaseToolkit(db=self.db, llm=self.llm).get_tools()
    
    def get_db(self):
        """
        Get the MySQL database connection
        
        Returns:
            SQLDatabase: Database connection instance
        """
        return self.db
    
    def get_schema_json(self) -> Dict[str, Any]:
        """
        Get the complete MySQL database schema in JSON format
        
        Returns:
            Dict[str, Any]: Dictionary containing all tables and their attributes
        """
        try:
            engine = self.db._engine
            
            # MySQL-specific query to get all tables and their columns with detailed information
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
                    WHEN pk.column_name IS NOT NULL THEN 1 
                    ELSE 0 
                END as is_primary_key,
                CASE 
                    WHEN fk.column_name IS NOT NULL THEN 1 
                    ELSE 0 
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
                    ku.referenced_table_name AS foreign_table_name,
                    ku.referenced_column_name AS foreign_column_name
                FROM 
                    information_schema.table_constraints tc
                JOIN 
                    information_schema.key_column_usage ku 
                    ON tc.constraint_name = ku.constraint_name
                WHERE 
                    tc.constraint_type = 'FOREIGN KEY'
            ) fk ON c.table_name = fk.table_name AND c.column_name = fk.column_name
            WHERE 
                t.table_schema = DATABASE() 
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
            raise Exception(f"Error extracting MySQL database schema: {str(e)}")
    
    def get_cached_schema_json(self) -> Dict[str, Any]:
        """
        Get the MySQL database schema from Redis cache or generate and cache it
        
        Returns:
            Dict[str, Any]: Dictionary containing all tables and their attributes
        """
        redis_client = get_redis_client()
        cache_key = f"mysql_schema:{self.db_url.split('/')[-1] if '/' in self.db_url else 'default'}"
        
        try:
            # Try to get from cache first
            cached_schema = redis_client.get(cache_key)
            
            if cached_schema:
                print(f"Using cached MySQL schema from Redis")
                return json.loads(cached_schema)
            
            # If not in cache, generate the schema
            print(f"No cached MySQL schema found in Redis. Generating new schema.")
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
            print(f"Redis cache error: {str(e)}. Falling back to direct MySQL schema generation.")
            return self.get_schema_json() 