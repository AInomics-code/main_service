#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.task_classifier.agent import TaskClassifierAgent

def test_task_classifier():
    agent = TaskClassifierAgent()
    
    test_inputs = [
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
    
    print("=== Probando TaskClassifierAgent con preguntas específicas ===\n")
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"Test {i:2d}:")
        print(f"Input: {user_input}")
        try:
            result = agent.classify_task(user_input)
            print(f"Resultado: {result}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 80)

def interactive_test():
    agent = TaskClassifierAgent()
    
    print("=== Modo Interactivo - TaskClassifierAgent ===")
    print("Escribe 'quit' para salir\n")
    
    while True:
        user_input = input("Ingresa tu pregunta: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'salir']:
            break
            
        if not user_input:
            continue
            
        try:
            result = agent.classify_task(user_input)
            print(f"Clasificación: {result}\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        test_task_classifier() 