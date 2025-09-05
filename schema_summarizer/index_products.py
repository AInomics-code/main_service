import os
import sys
import json
import logging
import time
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from typing import List, Dict, Any

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.simple_db_tool import create_database_tool
from config.settings import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductIndexer:
    """
    Indexa productos desde SQL Server hacia OpenSearch
    Basado en save_schema.py pero adaptado para productos
    """
    
    def __init__(self):
        self.opensearch_endpoint = settings.OPENSEARCH_ENDPOINT
        self.index_name = "productos"
        
        # Configurar herramienta de base de datos
        self.db_tool = create_database_tool(settings.SQLSERVER_URL)
        
        # Configurar autenticación AWS
        self.aws_credentials = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name='us-east-1'
        )
        
        # Configurar cliente OpenSearch
        self.opensearch_client = OpenSearch(
            hosts=[{'host': self.opensearch_endpoint.replace('https://', ''), 'port': 443}],
            http_auth=AWS4Auth(
                self.aws_credentials.get_credentials().access_key,
                self.aws_credentials.get_credentials().secret_key,
                'us-east-1',
                'aoss',
                session_token=self.aws_credentials.get_credentials().token
            ),
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
        
        # Configurar cliente Bedrock para Titan
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name='us-east-1',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

    def get_embeddings(self, text):
        """Obtener embeddings usando OpenAI como principal (igual que save_schema.py)"""
        try:
            # OpenAI como método principal
            from openai import OpenAI
            
            client = OpenAI(api_key=settings.OPENAI_KEY)
            response = client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except ImportError:
            # Si OpenAI no está disponible, intentar con Bedrock
            import json
            
            # Formato correcto para Titan v1
            request_body = {
                "inputText": text
            }
            
            response = self.bedrock_client.invoke_model(
                modelId='amazon.titan-embed-text-v1',
                body=json.dumps(request_body).encode('utf-8'),
                contentType='application/json'
            )
            response_body = response['body'].read()
            result = json.loads(response_body)
            return result['embedding']
        except Exception as e:
            logger.error(f"Error obteniendo embeddings: {e}")
            raise

    def get_products_from_sql(self) -> List[Dict[str, Any]]:
        """
        Obtiene TODOS los productos desde SQL Server (no solo 5 de muestra)
        """
        try:
            # Query simple - solo los campos que necesitamos
            sql_query = """
            SELECT producto_id, nombre 
            FROM productos
            """
            logger.info("Obteniendo TODOS los productos")
            
            # Acceder directamente a _execute_query para obtener todos los datos
            logger.info("Ejecutando consulta SQL...")
            result = self.db_tool._execute_query(sql_query, self.db_tool.default_connection_string)
            
            if result["success"]:
                logger.info(f"Consulta ejecutada exitosamente - {result['row_count']} productos encontrados")
                # Acceder directamente a todas las filas, no solo la muestra
                products = []
                for row_data in result['rows']:
                    if 'producto_id' in row_data and 'nombre' in row_data:
                        products.append(row_data)
                
                logger.info(f"Procesados {len(products)} productos correctamente")
                return products
            else:
                logger.error(f"Error en consulta SQL: {result['error']}")
                return []
                
        except Exception as e:
            logger.error(f"Error obteniendo productos desde SQL: {e}")
            return []

    def clear_products_index_serverless(self):
        """
        Limpia productos usando método compatible con OpenSearch Serverless
        """
        try:
            logger.info("🧹 Limpiando índice (método compatible con Serverless)...")
            
            # En OpenSearch Serverless, usamos búsqueda + borrado manual
            # Buscar todos los documentos primero
            search_query = {
                "query": {
                    "match_all": {}
                },
                "_source": False,  # Solo necesitamos los IDs
                "size": 1000  # Lote de 1000
            }
            
            deleted_count = 0
            
            # Buscar y borrar en lotes
            while True:
                response = self.opensearch_client.search(
                    index=self.index_name,
                    body=search_query
                )
                
                hits = response['hits']['hits']
                if not hits:
                    break
                
                # Borrar documentos por ID
                for hit in hits:
                    try:
                        self.opensearch_client.delete(
                            index=self.index_name,
                            id=hit['_id']
                        )
                        deleted_count += 1
                    except Exception as e:
                        logger.warning(f"No se pudo borrar documento {hit['_id']}: {e}")
                
                # Si obtuvimos menos documentos de los solicitados, hemos terminado
                if len(hits) < 1000:
                    break
            
            logger.info(f"✅ Eliminados {deleted_count} productos del índice")
            
            # Hacer refresh si es soportado
            try:
                self.opensearch_client.indices.refresh(index=self.index_name)
                logger.info("🔄 Índice refrescado")
            except Exception as e:
                logger.warning(f"Refresh no soportado en Serverless: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error limpiando índice: {e}")
            # No fallar por esto - continuamos sin limpiar
            logger.warning("⚠️ Continuando sin limpiar índice...")
            return True  # Retornamos True para continuar

    def verify_index_exists(self):
        """Verificar que el índice productos existe"""
        try:
            if not self.opensearch_client.indices.exists(index=self.index_name):
                logger.error(f"El índice {self.index_name} no existe")
                return False
            
            logger.info(f"Índice {self.index_name} existe")
            return True
            
        except Exception as e:
            logger.error(f"Error verificando índice: {e}")
            return False

    def index_product(self, producto_id: str, nombre_producto: str) -> bool:
        """
        Indexa un solo producto en OpenSearch
        """
        try:
            # Generar embeddings del nombre del producto
            logger.info(f"Generando embeddings para: {nombre_producto}")
            embeddings = self.get_embeddings(nombre_producto)
            
            # Preparar documento según el mapping actualizado
            document = {
                "producto_id": producto_id,  # Texto
                "nombre": embeddings  # Vector de embeddings
            }
            
            # Buscar si ya existe un producto con el mismo ID
            search_query = {
                "query": {
                    "term": {
                        "producto_id": producto_id
                    }
                }
            }
            
            search_result = self.opensearch_client.search(
                index=self.index_name,
                body=search_query,
                size=1
            )
            
            if search_result['hits']['total']['value'] > 0:
                # Producto existe, actualizar
                doc_id = search_result['hits']['hits'][0]['_id']
                self.opensearch_client.update(
                    index=self.index_name,
                    id=doc_id,
                    body={"doc": document}
                )
                logger.info(f"Producto {producto_id} actualizado")
            else:
                # Producto no existe, crear nuevo
                self.opensearch_client.index(
                    index=self.index_name,
                    body=document
                )
                logger.info(f"Producto {producto_id} creado")
            
            return True
            
        except Exception as e:
            logger.error(f"Error indexando producto {producto_id}: {e}")
            return False

    def index_product_direct(self, producto_id: str, nombre_producto: str) -> bool:
        """
        Indexa un producto directamente sin verificar si existe (para uso en batch)
        """
        try:
            # Generar embeddings del nombre del producto
            embeddings = self.get_embeddings(nombre_producto)
            
            # Preparar documento según el mapping actualizado
            document = {
                "producto_id": producto_id,  # Texto
                "nombre": embeddings  # Vector de embeddings
            }
            
            # Crear directamente sin verificar existencia
            self.opensearch_client.index(
                index=self.index_name,
                body=document
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error indexando producto directo {producto_id}: {e}")
            return False

    def index_all_products(self, batch_size: int = 100):
        """
        Limpia el índice y indexa TODOS los productos desde SQL Server hacia OpenSearch
        """
        try:
            # Verificar que el índice existe
            if not self.verify_index_exists():
                logger.error("No se puede proceder sin índice válido")
                return False
            
            # LIMPIAR índice antes de reindexar (compatible con Serverless)
            logger.info("🧹 Limpiando índice antes de reindexar...")
            if not self.clear_products_index_serverless():
                logger.error("No se pudo limpiar el índice")
                return False
            
            # Obtener productos desde SQL
            products = self.get_products_from_sql()
            
            if not products:
                logger.warning("No se encontraron productos para indexar")
                return False
            
            logger.info(f"🚀 Iniciando indexación de {len(products)} productos")
            
            # Indexar productos en lotes - sin verificar si existen (ya limpiamos el índice)
            success_count = 0
            error_count = 0
            
            for i, product in enumerate(products):
                producto_id = product.get('producto_id')
                nombre = product.get('nombre')
                
                if not producto_id or not nombre:
                    logger.warning(f"Producto incompleto: {product}")
                    error_count += 1
                    continue
                
                if self.index_product_direct(producto_id, nombre):
                    success_count += 1
                else:
                    error_count += 1
                
                # Mostrar progreso cada 50 productos
                if (i + 1) % 50 == 0:
                    logger.info(f"📈 Progreso: {i + 1}/{len(products)} productos procesados")
                
                # Refresh no siempre es necesario en Serverless
                if (i + 1) % batch_size == 0:
                    logger.info(f"🔄 Lote {i + 1} completado")
            
            # Pequeña pausa para que Serverless procese los datos
            time.sleep(1)
            logger.info("✅ Indexación completada - datos procesándose en Serverless")
            
            logger.info(f"🎯 Indexación completada. Éxitos: {success_count}, Errores: {error_count}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error en indexación masiva: {e}")
            return False

    def search_similar_products(self, query_text: str, top_k: int = 5):
        """
        Busca productos similares usando embeddings (para probar)
        """
        try:
            # Generar embeddings de la consulta
            query_embeddings = self.get_embeddings(query_text)
            
            # Query de búsqueda vectorial
            search_query = {
                "query": {
                    "knn": {
                        "nombre": {
                            "vector": query_embeddings,
                            "k": top_k
                        }
                    }
                },
                "_source": ["producto_id"],
                "size": top_k
            }
            
            response = self.opensearch_client.search(
                index=self.index_name,
                body=search_query
            )
            
            results = []
            for hit in response['hits']['hits']:
                results.append({
                    'producto_id': hit['_source']['producto_id'],
                    'score': hit['_score']
                })
            
            logger.info(f"Encontrados {len(results)} productos similares para: {query_text}")
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda de productos: {e}")
            return []

if __name__ == "__main__":
    # Ejemplo de uso
    print("🚀 Iniciando indexación de productos...")
    indexer = ProductIndexer()
    
    # Indexar todos los productos (limpia el índice automáticamente)
    success = indexer.index_all_products()
    
    if success:
        print("\n✅ Indexación completada exitosamente")
        
        # Probar búsqueda
        print("\n🔍 Probando búsqueda...")
        results = indexer.search_similar_products("mayonesa 350")
        for result in results:
            print(f"  - Producto ID: {result['producto_id']}, Score: {result['score']:.4f}")
    else:
        print("\n❌ Error en la indexación")
