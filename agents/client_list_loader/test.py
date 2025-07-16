#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.client_list_loader.agent import ClientListLoaderAgent

def test_client_list_loader():
    agent = ClientListLoaderAgent()
    
    test_inputs = [
        "Cuántos clientes activos tenemos en total?",
        "Muestra la cobertura de clientes por región",
        "Cuál es el porcentaje de cobertura del mercado?",
    ]
    
    print("=== Probando ClientListLoaderAgent con casos de prueba ===\n")
    
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
    agent = ClientListLoaderAgent()
    
    print("=== Modo Interactivo - ClientListLoaderAgent ===")
    print("Escribe 'quit' para salir\n")
    
    while True:
        user_input = input("Ingresa tu consulta de lista de clientes: ").strip()
        
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
        test_client_list_loader() 