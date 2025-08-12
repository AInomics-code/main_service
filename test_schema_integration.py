#!/usr/bin/env python3
"""
Script de prueba para verificar la integración del schema_summarizer
"""

import asyncio
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rest.invocation import invoke_agent
from fastapi import Request
from unittest.mock import AsyncMock

class MockRequest:
    def __init__(self, query):
        self.query = query
    
    async def json(self):
        return {"query": self.query}

async def test_schema_integration():
    """Prueba la integración del schema_summarizer"""
    
    print("🧪 Testing Schema Integration")
    print("=" * 50)
    
    # Query de prueba
    test_query = "¿Cuáles son los productos con mayor backorder en mi inventario?"
    
    print(f"📝 Test Query: {test_query}")
    print()
    
    # Crear request mock
    mock_request = MockRequest(test_query)
    
    try:
        # Ejecutar el agente
        print("🔄 Executing agent...")
        result = await invoke_agent(mock_request)
        
        print("✅ Agent execution completed!")
        print()
        
        # Mostrar resultados
        print("📊 RESULTS:")
        print(f"Input: {result['input']}")
        print(f"Schema Context Length: {len(result['schema_context'])}")
        print(f"Plan Steps: {len(result['plan'])}")
        
        if result['schema_context']:
            print("\n📋 SCHEMA CONTEXT:")
            print(result['schema_context'][:500] + "..." if len(result['schema_context']) > 500 else result['schema_context'])
        
        if result['plan']:
            print("\n📝 PLAN:")
            for i, step in enumerate(result['plan']):
                print(f"  {i+1}. {step}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting schema integration test...")
    asyncio.run(test_schema_integration())
