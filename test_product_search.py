#!/usr/bin/env python3
"""
Script de prueba simple para búsqueda semántica de productos
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.product_search_tools import get_best_product_id
from tools.database_tools import query_database

def test_mayonnaise_search():
    """Simple test: search for 'mayonnaise' and verify with SQL"""
    
    # Semantic search
    search_query = "mayonnaise 12oz"
    
    try:
        # Obtener el producto_id usando búsqueda semántica
        producto_id = get_best_product_id.invoke({"product_description": search_query})
        
        if producto_id.startswith("ERROR:") or producto_id.startswith("NO_ENCONTRADO:"):
            print(f"❌ {producto_id}")
            return
        
        if producto_id.startswith("COINCIDENCIA_DUDOSA:"):
            # Extraer el ID de la advertencia
            producto_id = producto_id.split(": ")[1].split(" ")[0]
        
        # Verify with SQL query
        sql_query = f"SELECT name FROM products WHERE product_id = '{producto_id}'"
        result = query_database.invoke({
            "query": sql_query,
            "db_type": "sqlite"
        })
        
        # Extraer nombre del producto del resultado
        nombre_real = "No encontrado"
        if "Row 1:" in result:
            import json
            try:
                # Buscar la línea que contiene Row 1:
                lines = result.split('\n')
                for line in lines:
                    if "Row 1:" in line:
                        json_part = line.split('Row 1: ')[1]
                        data = json.loads(json_part)
                        nombre_real = data.get('name', 'Not found')
                        break
            except:
                nombre_real = "Error parseando resultado"
        
        # Simple output
        print(f"User query: {search_query}")
        print(f"Product ID: {producto_id}")
        print(f"Real name: {nombre_real}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_mayonnaise_search()