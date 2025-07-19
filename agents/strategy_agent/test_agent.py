#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.strategy_agent.agent import StrategyAgent

def test_strategy_agent():
    agent = StrategyAgent()
    
    test_inputs = [
        "¿Cuantos clientes en total hay?"
    ]

    print("=== Probando StrategyAgent con casos de prueba ===\n")
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"Test {i:2d}:")
        print(f"Input: {user_input}")
        try:
            result = agent.run(user_input)
            print(f"Resultado: {result}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 80)

def test_synthesize_results():
    agent = StrategyAgent()
    
    test_inputs = [
        "Sintetiza los resultados de ventas y finanzas",
        "Combina el análisis de inventario y operaciones de campo"
    ]
    
    mock_results = "Ventas: $100,000, Finanzas: ROI 15%, Inventario: 80% disponible"

    print("=== Probando StrategyAgent synthesize_results ===\n")
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"Test {i:2d}:")
        print(f"Input: {user_input}")
        try:
            result = agent.synthesize_results(user_input, mock_results)
            print(f"Resultado: {result}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 80)

def interactive_test():
    agent = StrategyAgent()
    
    print("=== Modo Interactivo - StrategyAgent ===")
    print("Escribe 'quit' para salir\n")
    
    while True:
        user_input = input("Ingresa tu consulta estratégica: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'salir']:
            break
            
        if not user_input:
            continue
            
        try:
            result = agent.run(user_input)
            print(f"Resultado: {result}\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    elif len(sys.argv) > 1 and sys.argv[1] == "--synthesize":
        test_synthesize_results()
    else:
        test_strategy_agent() 