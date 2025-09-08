from langchain_core.tools import tool
import sqlite3
import json
import logging

logger = logging.getLogger(__name__)

@tool
def query_database(query: str, db_type: str = "sqlite") -> str:
    """
    Ejecuta una consulta SQL en la base de datos SQLite demo
    
    Args:
        query: Consulta SQL a ejecutar
        db_type: Tipo de base de datos (solo sqlite para demo)
    
    Returns:
        Resultado de la consulta en formato JSON
    """
    print(f"\n🗄️ QUERY_DATABASE TOOL CALLED")
    print(f"   Database: {db_type} (demo)")
    print(f"   📊 SQL Query:")
    print(f"   {query}")
    print(f"   " + "="*50)
    
    try:
        # Track SQL query in global memory if available
        from rest.invocation import current_memory
        if current_memory:
            current_memory.add_executed_sql(query)
            print(f"   📝 SQL tracked in sources")
        
        # Simple SQLite connection for demo
        conn = sqlite3.connect('demo_database.db')
        cursor = conn.cursor()
        
        cursor.execute(query)
        
        # Get column names
        columns = [description[0] for description in cursor.description] if cursor.description else []
        
        # Fetch results
        rows = cursor.fetchall()
        
        # Convert to JSON format similar to the original tool
        result_rows = []
        for row in rows:
            row_dict = {}
            for i, value in enumerate(row):
                if i < len(columns):
                    row_dict[columns[i]] = value
            result_rows.append(row_dict)
        
        conn.close()
        
        # Format response
        response = f"Query executed successfully\nRows returned: {len(result_rows)}\n\n"
        
        if result_rows:
            response += "Sample results:\n"
            for i, row in enumerate(result_rows[:5], 1):
                response += f"Row {i}: {json.dumps(row, default=str)}\n"
            
            if len(result_rows) > 5:
                response += f"\n... and {len(result_rows) - 5} more rows"
        else:
            response += "No rows returned"
        
        print(f"   ✅ Query executed successfully")
        print(f"   📈 Result preview: {response[:200]}...")
        
        return response
        
    except Exception as e:
        print(f"   ❌ Database query error: {e}")
        logger.error(f"Database query error: {e}")
        return f"Error executing query: {str(e)}"
