from langchain.utilities import SQLDatabase
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
import os
from typing import Optional
from langchain.base_language import BaseLanguageModel

from config.settings import settings

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