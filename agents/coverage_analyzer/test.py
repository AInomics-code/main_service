#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.coverage_analyzer.agent import CoverageAnalyzerAgent

def test_coverage_analyzer():
    agent = CoverageAnalyzerAgent()
    
    test_inputs = [
        "Cuál es el porcentaje de cobertura del mercado actual?",
        "Muestra los clientes faltantes por territorio",
        "Cuáles son las áreas con menor cobertura?",
    ]
    
    print("=== Probando CoverageAnalyzerAgent con casos de prueba ===\n")
    
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
    agent = CoverageAnalyzerAgent()
    
    print("=== Modo Interactivo - CoverageAnalyzerAgent ===")
    print("Escribe 'quit' para salir\n")
    
    while True:
        user_input = input("Ingresa tu consulta de análisis de cobertura: ").strip()
        
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
        test_coverage_analyzer() 