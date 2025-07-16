#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.cost_margin_fetcher.agent import CostMarginFetcherAgent

def test_cost_margin_fetcher():
    agent = CostMarginFetcherAgent()
    
    test_inputs = [
        "Cuál es el margen bruto y neto del mes actual?",
        "Muestra la rentabilidad de los productos más vendidos",
        "Cuáles son los costos que más impactan la rentabilidad?",
    ]
    
    print("=== Probando CostMarginFetcherAgent con casos de prueba ===\n")
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"Test {i}:")
        print(f"Input: {user_input}")
        try:
            result = agent.run(user_input)
            print(f"Respuesta:")
            print(result)
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 80)

def interactive_test():
    agent = CostMarginFetcherAgent()
    
    print("=== Modo Interactivo - CostMarginFetcherAgent ===")
    print("Escribe 'quit' para salir\n")
    
    while True:
        user_input = input("Ingresa tu consulta de costos y márgenes: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'salir']:
            break
            
        if not user_input:
            continue
            
        try:
            result = agent.run(user_input)
            print(f"Respuesta:")
            print(result)
            print()
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        test_cost_margin_fetcher() 