import os
import sys
import json
import boto3
import time
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# Agregar el directorio padre al path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

class TableFinder:
    def __init__(self):
        print("Inicializando TableFinder...")
        self.opensearch_endpoint = settings.OPENSEARCH_ENDPOINT
        self.index_name = "tables"
        
        print(f"OpenSearch endpoint: {self.opensearch_endpoint}")
        print(f"Index name: {self.index_name}")
        
        # Configurar autenticación AWS
        print("Configurando credenciales AWS...")
        self.aws_credentials = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name='us-east-1'
        )
        
        # Configurar cliente OpenSearch con timeouts optimizados
        print("Configurando cliente OpenSearch...")
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
            connection_class=RequestsHttpConnection,
            timeout=5,  # Timeout más agresivo
            max_retries=1,  # Menos reintentos
            retry_on_timeout=False
        )
        
        # Configurar cliente Bedrock para Titan
        print("Configurando cliente Bedrock...")
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name='us-east-1',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=boto3.session.Config(
                connect_timeout=3,
                read_timeout=5
            )
        )
        print("TableFinder inicializado correctamente")

    def get_embeddings(self, text):
        """Obtener embeddings usando Titan v1 - optimizado para velocidad"""
        try:
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
            print(f"Error obteniendo embeddings: {e}")
            raise

    def test_simple_search(self):
        """Test simple para diagnosticar problemas de OpenSearch"""
        try:
            print("🔍 Probando búsqueda simple...")
            start_time = time.time()
            
            # Búsqueda simple sin vectores
            query_body = {
                "query": {
                    "match_all": {}
                },
                "size": 5
            }
            
            response = self.opensearch_client.search(
                index=self.index_name,
                body=query_body,
                request_timeout=5
            )
            
            search_time = time.time() - start_time
            print(f"   ✅ Búsqueda simple completada en {search_time:.3f}s")
            print(f"   📊 Documentos encontrados: {len(response['hits']['hits'])}")
            
            return search_time
            
        except Exception as e:
            print(f"❌ Error en búsqueda simple: {e}")
            return None

    def find_best_tables(self, user_question, k=5):
        """Encontrar las mejores tablas para una pregunta del usuario - optimizado para velocidad"""
        start_time = time.time()
        
        try:
            print(f"Buscando tablas para: '{user_question}'")
            
            # Obtener embeddings de la pregunta del usuario
            print("1. Generando embeddings de la consulta...")
            start_embedding = time.time()
            query_embedding = self.get_embeddings(user_question)
            embedding_time = time.time() - start_embedding
            print(f"   ✅ Embeddings generados en {embedding_time:.3f}s")
            
            print("2. Preparando query...")
            start_query = time.time()
            # Query de búsqueda vectorial optimizada
            query_body = {
                "query": {
                    "knn": {
                        "embedding": {
                            "vector": query_embedding,
                            "k": k
                        }
                    }
                },
                "_source": ["table_name", "content"],
                "size": k
            }
            query_prep_time = time.time() - start_query
            print(f"   ✅ Query preparada en {query_prep_time:.3f}s")
            
            print("3. Ejecutando búsqueda en OpenSearch...")
            start_search = time.time()
            # Realizar búsqueda con timeout muy corto
            response = self.opensearch_client.search(
                index=self.index_name,
                body=query_body,
                request_timeout=3  # Timeout muy corto
            )
            search_time = time.time() - start_search
            print(f"   ✅ Búsqueda completada en {search_time:.3f}s")
            
            print("4. Procesando resultados...")
            start_process = time.time()
            hits = response['hits']['hits']
            process_time = time.time() - start_process
            print(f"   ✅ Resultados procesados en {process_time:.3f}s")
            
            print(f"\nTop {len(hits)} tablas para tu pregunta:")
            print("-" * 40)
            
            for i, hit in enumerate(hits, 1):
                score = hit['_score']
                table_name = hit['_source']['table_name']
                content = hit['_source']['content'][:100] + "..." if len(hit['_source']['content']) > 100 else hit['_source']['content']
                
                print(f"{i}. {table_name} (score: {score:.2f})")
                print(f"   {content}")
                print()
            
            total_time = time.time() - start_time
            print(f"⏱️  TIEMPOS:")
            print(f"   - Embeddings: {embedding_time:.3f}s")
            print(f"   - Búsqueda OpenSearch: {search_time:.3f}s")
            print(f"   - Procesamiento: {process_time:.3f}s")
            print(f"   - TOTAL: {total_time:.3f}s")
            
            return hits
                
        except Exception as e:
            total_time = time.time() - start_time
            print(f"❌ Error en {total_time:.3f}s: {e}")
            raise

def main():
    """Función principal para probar la herramienta"""
    print("🚀 Iniciando búsqueda rápida de tablas...")
    finder = TableFinder()
    
    # Test de diagnóstico primero
    print("\n" + "="*50)
    print("🔧 DIAGNÓSTICO DE VELOCIDAD")
    print("="*50)
    simple_time = finder.test_simple_search()
    
    if simple_time and simple_time > 1.0:
        print(f"⚠️  ADVERTENCIA: Búsqueda simple tardó {simple_time:.3f}s (debería ser < 1s)")
    else:
        print(f"✅ Búsqueda simple OK: {simple_time:.3f}s")
    
    print("\n" + "="*50)
    print("🔍 BÚSQUEDA VECTORIAL")
    print("="*50)
    
    # Ejemplo de uso - solo top 5 tablas
    user_question = "cual es el backorder total del mes de julio del 2025?"
    
    print("🔍 Buscando top 5 tablas...")
    finder.find_best_tables(user_question, k=5)
    print("✅ Búsqueda completada")

if __name__ == "__main__":
    main()
