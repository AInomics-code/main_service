#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.attendance_checker.agent import AttendanceCheckerAgent

def test_attendance_checker():
    agent = AttendanceCheckerAgent()
    
    test_inputs = [
        "Cuántos representantes llegaron tarde hoy?",
        "Muestra los clientes visitados sin orden generada",
        "Cuál es el porcentaje de asistencia del equipo de ventas?",
    ]
    
    print("=== Probando AttendanceCheckerAgent con casos de prueba ===\n")
    
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
    agent = AttendanceCheckerAgent()
    
    print("=== Modo Interactivo - AttendanceCheckerAgent ===")
    print("Escribe 'quit' para salir\n")
    
    while True:
        user_input = input("Ingresa tu consulta de asistencia: ").strip()
        
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
        test_attendance_checker() 