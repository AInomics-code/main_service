#!/usr/bin/env python3
"""
Test del flujo completo con el agente de invocación
"""

import json
import asyncio
from fastapi import Request
from rest.invocation import invoke_agent

class MockRequest:
    """Mock request para testing"""
    def __init__(self, data):
        self.data = data
    
    async def json(self):
        return self.data

async def test_full_agent_flow():
    """Prueba el flujo completo del agente con búsqueda de productos"""
    
    print("🧪 Test del flujo completo del agente\n")
    
    # Simulate request
    test_query = "how many Hellmanns mayonnaise units did we sell last month?"
    
    mock_request = MockRequest({
        "message": test_query
    })
    
    print(f"📝 Enviando consulta: '{test_query}'")
    print("=" * 60)
    
    try:
        # Invocar el agente completo
        result = await invoke_agent(mock_request)
        
        print("✅ RESULTADO DEL AGENTE:")
        print(f"Plan ejecutado: {len(result.get('plan', []))} pasos")
        
        for i, step in enumerate(result.get('plan', []), 1):
            print(f"   {i}. {step}")
        
        print(f"\nRespuesta final:")
        print("-" * 40)
        print(result.get('response', 'No response'))
        
        print(f"\nSQL ejecutados:")
        for i, sql in enumerate(result.get('sources', []), 1):
            print(f"   {i}. {sql[:100]}...")
        
        print(f"\n🎯 VERIFICACIÓN:")
        response = result.get('response', '').lower()
        
        # Verificar que mencionó búsqueda de productos
        if any(keyword in response for keyword in ['producto', 'mayonesa', 'bodega']):
            print("✅ El agente procesó correctamente la consulta de producto")
        else:
            print("⚠️ La respuesta no parece relacionada con productos")
        
        # Verificar que usó SQL
        if result.get('sources'):
            print("✅ El agente ejecutó consultas SQL")
        else:
            print("⚠️ No se ejecutaron consultas SQL")
        
    except Exception as e:
        print(f"❌ Error en el test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Iniciando test del flujo completo...")
    asyncio.run(test_full_agent_flow())
