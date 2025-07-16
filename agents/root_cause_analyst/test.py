#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.root_cause_analyst.agent import RootCauseAnalystAgent

def test_root_cause_analyst():
    agent = RootCauseAnalystAgent()
    
    test_inputs = [
        "¿Por qué bajaron las ventas en el último mes?",
        "Analiza las causas del bajo rendimiento en la región norte",
        "¿Cuáles son los factores que contribuyeron al crecimiento?",
    ]
    
    print("=== Probando RootCauseAnalystAgent con casos de prueba ===\n")
    
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
    agent = RootCauseAnalystAgent()
    
    print("=== Modo Interactivo - RootCauseAnalystAgent ===")
    print("Escribe 'quit' para salir\n")
    
    while True:
        user_input = input("Ingresa tu consulta de análisis de causa raíz: ").strip()
        
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
        test_root_cause_analyst() 