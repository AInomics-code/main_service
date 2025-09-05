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

def test_mayonesa_search():
    """Prueba simple: buscar 'mayonesa 350' y verificar con SQL"""
    
    # Búsqueda semántica
    search_query = "mayonesa 350gr"
    
    try:
        # Obtener el producto_id usando búsqueda semántica
        producto_id = get_best_product_id.invoke({"product_description": search_query})
        
        if producto_id.startswith("ERROR:") or producto_id.startswith("NO_ENCONTRADO:"):
            print(f"❌ {producto_id}")
            return
        
        if producto_id.startswith("COINCIDENCIA_DUDOSA:"):
            # Extraer el ID de la advertencia
            producto_id = producto_id.split(": ")[1].split(" ")[0]
        
        # Verificar con consulta SQL
        sql_query = f"SELECT nombre FROM productos WHERE producto_id = '{producto_id}'"
        result = query_database.invoke({
            "query": sql_query,
            "db_type": "sqlserver"
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
                        nombre_real = data.get('nombre', 'No encontrado')
                        break
            except:
                nombre_real = "Error parseando resultado"
        
        # Salida simple
        print(f"Pregunta usuario: {search_query}")
        print(f"ID producto: {producto_id}")
        print(f"Nombre real: {nombre_real}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_mayonesa_search()