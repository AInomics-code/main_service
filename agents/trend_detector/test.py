#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.trend_detector.agent import TrendDetectorAgent

def test_trend_detector():
    agent = TrendDetectorAgent()
    
    test_inputs = [
        "¿Cuál es la tendencia de ventas en los últimos 6 meses?",
        "Muestra la tendencia de crecimiento por región",
        "¿Hay alguna tendencia estacional en los datos?",
    ]
    
    print("=== Probando TrendDetectorAgent con casos de prueba ===\n")
    
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
    agent = TrendDetectorAgent()
    
    print("=== Modo Interactivo - TrendDetectorAgent ===")
    print("Escribe 'quit' para salir\n")
    
    while True:
        user_input = input("Ingresa tu consulta de análisis de tendencias: ").strip()
        
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
        test_trend_detector() 