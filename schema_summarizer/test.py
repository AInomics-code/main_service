#!/usr/bin/env python3
"""
Test script para la herramienta SchemaSummarizer.
Mide el tiempo de búsqueda semántica y retorna las tablas más relevantes para cada pregunta.
"""

import time
from schema_summarizer import SchemaSummarizer

def test_schema_summarizer():
    """
    Función principal de test que prueba las preguntas específicas.
    """
    
    print("=== TEST DE SCHEMA SUMMARIZER ===\n")
    
    # Inicializar la herramienta
    print("1. Inicializando SchemaSummarizer...")
    summarizer = SchemaSummarizer()
    
    # Construir el índice vectorial (setup - no se mide)
    print("2. Construyendo índice vectorial...")
    summarizer.build_vector_index()
    
    # Array de preguntas de prueba
    test_queries = [
        "¿Qué cadena está por debajo del presupuesto?",
        "¿Qué producto no se vendió el día de ayer / por semana / por punto de venta (PDV)?",
        "De las promociones scanner ofrecidas el mes anterior, ¿cuál fue la más vendida?",
        "Según la inversión en tongas/muebles, ¿cuál PDV es más rentable?",
        "¿Qué productos están decreciendo o creciendo vs el mes/trimestre/año pasado?",
        "¿Cuál es el producto más vendido por cadena?",
        "Del censo nacional de clientes de Dichter, ¿a cuántos no les vendemos? Dame la lista con geolocalización.",
        "¿Qué productos sugieres descatalogar por poca venta?",
        "Según presupuesto de inversión por cadena, ¿dónde me estoy pasando?",
        "¿Qué cadena está morosa a más de 120 días?",
        "Durante esta última quincena/mes/trimestre, ¿cuáles vendedores han llegado tarde?",
        "¿Qué productos no tenemos en inventario en las sucursales?",
        "Según la madre (categoría principal), ¿qué productos están por debajo esta semana en sucursales?",
        "¿Cómo va el crecimiento en ventas vs el año pasado por cadena?",
        "¿Cómo va el crecimiento en ventas vs el año pasado de los clientes de exportación? ¿Y de EPA?",
        "¿Cuántos SKUs tenemos por canal? ¿Y cuántos en total en la compañía?",
        "¿Cuántos clientes activos tenemos en total? ¿Y por sucursal?",
        "¿Cuántos PDVs debería atender un vendedor por día según ruta/venta?",
        "¿Cuál es la rentabilidad por SKU?",
        "¿Cuánto están creciendo los productos de maquilas de la cadena Dichter vs el año pasado?",
        "Facilítame el número de extensión/celular/correo electrónico de Juan Perez.",
        "Facilítame el arte de la mayonesa.",
        "Facilítame el código de barra de la mayonesa.",
        "Facilítame el precio de la mayonesa en la cadena tal o en el cliente tal.",
        "¿Cuál es el BO (backorder) de hoy?",
        "¿Cuánto va la facturación hoy?",
        "¿Qué clientes se han facturado hoy?",
        "¿Qué ruta tiene el vendedor Juan Perez hoy?",
        "Según el rutero de visita por vendedor hoy, ¿qué clientes no realizaron pedido? ¿Por qué?"
    ]
    
    print(f"\n3. Probando {len(test_queries)} consultas específicas...\n")
    
    # Pausa para separar tiempo de carga del tiempo de ejecución
    input("Presiona cualquier tecla para comenzar las consultas...")
    
    print("RESULTADOS:")
    print("=" * 80)
    
    # Probar cada consulta
    for i, query in enumerate(test_queries, 1):
        print(f"{i:2d}. Pregunta: {query}")
        
        try:
            # Medir solo el tiempo de búsqueda semántica
            start_time = time.time()
            relevant_tables = summarizer.search_relevant_tables(query, top_k=5)
            end_time = time.time()
            
            search_time = (end_time - start_time) * 1000  # Convertir a milisegundos
            
            # Extraer solo los nombres de las tablas
            table_names = [table['table_name'] for table in relevant_tables]
            
            print(f"    Tablas: {', '.join(table_names)}")
            print(f"    Tiempo: {search_time:.2f} ms")
            print()
            
        except Exception as e:
            print(f"    Error: {str(e)}")
            print()
    
    print("=" * 80)
    print("TEST COMPLETADO")

if __name__ == "__main__":
    test_schema_summarizer() 