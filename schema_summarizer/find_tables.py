import os
import sys
import json
import boto3
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
        
        # Configurar cliente OpenSearch (igual que en save_schema.py)
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
            connection_class=RequestsHttpConnection
        )
        
        # Configurar cliente Bedrock para Titan
        print("Configurando cliente Bedrock...")
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name='us-east-1',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        print("TableFinder inicializado correctamente")

    def get_embeddings(self, text):
        """Obtener embeddings usando Titan v1"""
        try:
            print(f"Obteniendo embeddings para: '{text[:50]}...'")
            request_body = {
                "inputText": text
            }
            
            print("Llamando a Bedrock...")
            response = self.bedrock_client.invoke_model(
                modelId='amazon.titan-embed-text-v1',
                body=json.dumps(request_body).encode('utf-8'),
                contentType='application/json'
            )
            print("Respuesta de Bedrock recibida")
            
            response_body = response['body'].read()
            result = json.loads(response_body)
            embedding = result['embedding']
            print(f"Embeddings obtenidos, longitud: {len(embedding)}")
            return embedding
        except Exception as e:
            print(f"Error obteniendo embeddings: {e}")
            raise

    def find_best_tables(self, user_question, k=5):
        """Encontrar las mejores tablas para una pregunta del usuario"""
        try:
            print(f"Buscando tablas para: '{user_question}'")
            
            # Obtener embeddings de la pregunta del usuario
            query_embedding = self.get_embeddings(user_question)
            
            print("Realizando búsqueda en OpenSearch...")
            
            # Query de búsqueda vectorial usando la sintaxis correcta para k-NN
            query_body = {
                "knn": {
                    "field": "embeddings",
                    "query_vector": query_embedding,
                    "k": k,
                    "num_candidates": 50
                },
                "_source": ["table_name", "content"]
            }
            
            # Realizar búsqueda usando el cliente OpenSearch
            response = self.opensearch_client.search(
                index=self.index_name,
                body=query_body
            )
            
            print(f"Respuesta recibida, hits encontrados: {len(response['hits']['hits'])}")
            
            hits = response['hits']['hits']
            
            print(f"Mejores {len(hits)} tablas para tu pregunta: '{user_question}'")
            print("-" * 50)
            
            for i, hit in enumerate(hits, 1):
                score = hit['_score']
                table_name = hit['_source']['table_name']
                content = hit['_source']['content'][:200] + "..." if len(hit['_source']['content']) > 200 else hit['_source']['content']
                
                print(f"{i}. Tabla: {table_name}")
                print(f"   Score: {score:.4f}")
                print(f"   Descripción: {content}")
                print()
            
            return hits
                
        except Exception as e:
            print(f"Error buscando tablas: {e}")
            import traceback
            traceback.print_exc()
            raise

def main():
    """Función principal para probar la herramienta"""
    print("Iniciando búsqueda de tablas...")
    finder = TableFinder()
    
    # Ejemplo de uso
    user_question = "Necesito información sobre transacciones de materiales"
    
    print("Buscando mejores tablas...")
    finder.find_best_tables(user_question)
    print("Búsqueda completada")

if __name__ == "__main__":
    main()
