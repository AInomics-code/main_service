import sys
import os
from langchain_core.tools import tool
from typing import List, Dict, Any
import logging

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema_summarizer.index_products import ProductIndexer
from config.settings import settings

logger = logging.getLogger(__name__)

# Instancia global del indexer para reutilizar conexión
_product_indexer = None

def get_product_indexer():
    """Obtiene o crea la instancia del ProductIndexer"""
    global _product_indexer
    if _product_indexer is None:
        _product_indexer = ProductIndexer()
    return _product_indexer

@tool
def find_product_by_name(product_description: str, max_results: int = 3) -> str:
    """
    Busca productos usando búsqueda semántica basada en la descripción del usuario.
    
    Esta herramienta resuelve el problema de que los usuarios no usan nombres exactos de productos.
    Ejemplo: "mayonesa de 350grs" → encuentra "Mayonesa HELLMANN'S 350g" y retorna su producto_id.
    
    Args:
        product_description: Descripción del producto como la menciona el usuario
        max_results: Número máximo de resultados a retornar (default: 3)
    
    Returns:
        JSON string con los productos encontrados y sus IDs para usar en consultas SQL
    """
    try:
        logger.info(f"🔍 Buscando productos similares a: '{product_description}'")
        
        # Obtener instancia del indexer
        indexer = get_product_indexer()
        
        # Buscar productos similares usando embeddings
        results = indexer.search_similar_products(product_description, top_k=max_results)
        
        if not results:
            logger.warning(f"❌ No se encontraron productos similares para: '{product_description}'")
            return f"No se encontraron productos similares para '{product_description}'. Verifica la descripción o usa términos más generales."
        
        # Formatear resultados para usar en SQL
        found_products = []
        for i, result in enumerate(results):
            found_products.append({
                "producto_id": result['producto_id'],
                "similarity_score": round(result['score'], 4),
                "rank": i + 1
            })
        
        logger.info(f"✅ Encontrados {len(found_products)} productos similares")
        
        # Preparar respuesta detallada
        response = f"Productos encontrados para '{product_description}':\n\n"
        
        best_match = found_products[0]
        response += f"🎯 MEJOR COINCIDENCIA:\n"
        response += f"   - Producto ID: {best_match['producto_id']}\n"
        response += f"   - Score de similitud: {best_match['similarity_score']}\n\n"
        
        if len(found_products) > 1:
            response += f"📋 OTRAS OPCIONES:\n"
            for product in found_products[1:]:
                response += f"   {product['rank']}. ID: {product['producto_id']} (Score: {product['similarity_score']})\n"
            response += "\n"
        
        response += f"💡 USO EN SQL:\n"
        response += f"   WHERE producto_id = '{best_match['producto_id']}'\n"
        
        # Crear lista de IDs para uso múltiple
        product_ids = [p['producto_id'] for p in found_products]
        ids_list = "', '".join(product_ids)
        response += f"   OR usa múltiples: WHERE producto_id IN ('{ids_list}')\n\n"
        
        response += f"🔧 DATOS ESTRUCTURADOS:\n{found_products}"
        
        return response
        
    except Exception as e:
        logger.error(f"Error en búsqueda de productos: {e}")
        return f"Error buscando productos: {str(e)}. Verifica que el índice de productos esté disponible."

@tool  
def get_best_product_id(product_description: str) -> str:
    """
    Obtiene SOLO el producto_id de la mejor coincidencia para un producto.
    
    Versión simplificada de find_product_by_name que retorna únicamente el ID
    del producto más similar para uso directo en consultas SQL.
    
    Args:
        product_description: Descripción del producto como la menciona el usuario
        
    Returns:
        String con el producto_id de la mejor coincidencia o mensaje de error
    """
    try:
        logger.info(f"🎯 Obteniendo mejor producto ID para: '{product_description}'")
        
        # Obtener instancia del indexer
        indexer = get_product_indexer()
        
        # Buscar solo la mejor coincidencia
        results = indexer.search_similar_products(product_description, top_k=1)
        
        if not results:
            return f"NO_ENCONTRADO: '{product_description}'"
        
        best_match = results[0]
        producto_id = best_match['producto_id']
        score = round(best_match['score'], 4)
        
        logger.info(f"✅ Mejor coincidencia: {producto_id} (score: {score})")
        
        # Si el score es muy bajo, advertir
        if score < 0.5:
            return f"COINCIDENCIA_DUDOSA: {producto_id} (score: {score}) para '{product_description}'"
        
        return producto_id
        
    except Exception as e:
        logger.error(f"Error obteniendo producto ID: {e}")
        return f"ERROR: {str(e)}"

@tool
def search_products_batch(product_descriptions: List[str], max_results_per_product: int = 2) -> str:
    """
    Busca múltiples productos en una sola llamada para optimizar rendimiento.
    
    Args:
        product_descriptions: Lista de descripciones de productos
        max_results_per_product: Máximo de resultados por producto
        
    Returns:
        JSON string con todos los resultados organizados por descripción
    """
    try:
        logger.info(f"🔍 Búsqueda en lote de {len(product_descriptions)} productos")
        
        indexer = get_product_indexer()
        batch_results = {}
        
        for description in product_descriptions:
            try:
                results = indexer.search_similar_products(description, top_k=max_results_per_product)
                
                batch_results[description] = {
                    "found": len(results) > 0,
                    "best_product_id": results[0]['producto_id'] if results else None,
                    "best_score": round(results[0]['score'], 4) if results else None,
                    "all_results": results
                }
                
            except Exception as e:
                logger.error(f"Error buscando '{description}': {e}")
                batch_results[description] = {
                    "found": False,
                    "error": str(e),
                    "best_product_id": None
                }
        
        logger.info(f"✅ Búsqueda en lote completada")
        
        # Formatear respuesta
        response = "Resultados de búsqueda en lote:\n\n"
        
        for description, result in batch_results.items():
            response += f"'{description}': "
            if result['found']:
                response += f"✅ {result['best_product_id']} (score: {result['best_score']})\n"
            else:
                response += f"❌ No encontrado\n"
        
        response += f"\n🔧 DATOS ESTRUCTURADOS:\n{batch_results}"
        
        return response
        
    except Exception as e:
        logger.error(f"Error en búsqueda batch: {e}")
        return f"Error en búsqueda batch: {str(e)}"

# Herramienta de utilidad para verificar estado del índice
@tool
def check_product_index_status() -> str:
    """
    Verifica el estado del índice de productos en OpenSearch.
    
    Returns:
        String con información sobre el estado del índice
    """
    try:
        indexer = get_product_indexer()
        
        if not indexer.verify_index_exists():
            return "❌ El índice de productos no existe. Ejecuta el script de indexación primero."
        
        # Hacer una búsqueda de prueba para verificar que funciona
        test_results = indexer.search_similar_products("test", top_k=1)
        
        if test_results:
            return f"✅ Índice de productos funcionando correctamente. Productos disponibles para búsqueda."
        else:
            return "⚠️ Índice existe pero parece estar vacío. Considera reindexar los productos."
            
    except Exception as e:
        return f"❌ Error verificando índice: {str(e)}"
