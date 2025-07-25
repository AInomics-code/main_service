#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.sales_agent.agent import SalesAgent

def test_sales_agent():
    agent = SalesAgent()
    
    test_inputs = [
        "Cuantas ventas en total hay?",
    ]

    print("=== Probando SalesAgent con casos de prueba ===\n")
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"Test {i:2d}:")
        print(f"Input: {user_input}")
        try:
            result = agent.run(user_input)
            print(f"Resultado: {result}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 80)

def interactive_test():
    agent = SalesAgent()
    
    print("=== Modo Interactivo - SalesAgent ===")
    print("Escribe 'quit' para salir\n")
    
    while True:
        user_input = input("Ingresa tu consulta de ventas: ").strip()
        
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
    else:
        test_sales_agent() 