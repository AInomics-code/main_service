#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.ar_aging_agent.agent import ARAgingAgent

def test_ar_aging_agent():
    agent = ARAgingAgent()
    
    test_inputs = [
        "Cuál es el envejecimiento de cuentas por cobrar actual?",
        "Muestra las cuentas vencidas por más de 90 días",
        "Cuál es el total de cuentas por cobrar vencidas?",
    ]
    
    print("=== Probando ARAgingAgent con casos de prueba ===\n")
    
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
    agent = ARAgingAgent()
    
    print("=== Modo Interactivo - ARAgingAgent ===")
    print("Escribe 'quit' para salir\n")
    
    while True:
        user_input = input("Ingresa tu consulta de AR Aging: ").strip()
        
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
        test_ar_aging_agent() 