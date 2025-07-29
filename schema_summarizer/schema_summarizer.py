import os
import sys
import json
import boto3
import time
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from typing import List, Dict, Any, Tuple

# Agregar el directorio padre al path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

class SchemaSummarizer:
    """
    Herramienta para optimizar el envío de esquemas de base de datos a los agentes.
    Usa OpenSearch y Bedrock para búsqueda semántica rápida en la nube.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SchemaSummarizer, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, schema_folder: str = None):
        """
        Inicializa el SchemaSummarizer (Singleton).
        """
        if self._initialized:
            return
        
        # Si no se especifica schema_folder, usar la ruta relativa al módulo
        if schema_folder is None:
            # Obtener la ruta del directorio donde está este archivo
            current_dir = os.path.dirname(os.path.abspath(__file__))
            schema_folder = os.path.join(current_dir, "schema_files")
            
        self.schema_folder = schema_folder
        self.opensearch_endpoint = settings.OPENSEARCH_ENDPOINT
        self.index_name = "tables"
        
        # Configurar autenticación AWS
        self.aws_credentials = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name='us-east-1'
        )
        
        # Configurar cliente OpenSearch con timeouts optimizados
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
        
        SchemaSummarizer._initialized = True
        print("SchemaSummarizer inicializado correctamente con OpenSearch")
    
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
    
    def search_relevant_tables(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Busca las tablas más relevantes para una consulta dada usando OpenSearch.
        
        Args:
            query: Consulta del usuario
            top_k: Número máximo de resultados a retornar
            
        Returns:
            Lista de diccionarios con información de las tablas más relevantes
        """
        try:
            # Obtener embeddings de la pregunta del usuario
            query_embedding = self.get_embeddings(query)
            
            # Query de búsqueda vectorial optimizada
            query_body = {
                "query": {
                    "knn": {
                        "embedding": {
                            "vector": query_embedding,
                            "k": top_k
                        }
                    }
                },
                "_source": ["table_name", "content"],
                "size": top_k
            }
            
            # Realizar búsqueda con timeout muy corto
            response = self.opensearch_client.search(
                index=self.index_name,
                body=query_body,
                request_timeout=3  # Timeout muy corto
            )
            
            hits = response['hits']['hits']
            results = []
            
            for i, hit in enumerate(hits):
                score = hit['_score']
                table_name = hit['_source']['table_name']
                content = hit['_source']['content']
                
                results.append({
                    'rank': i + 1,
                    'table_name': table_name,
                    'content': content,
                    'relevance_score': float(score),
                    'file_path': os.path.join(self.schema_folder, f"{table_name}.txt")
                })
            
            return results
                
        except Exception as e:
            print(f"Error en búsqueda de tablas relevantes: {e}")
            return []
    
    def get_schema_summary(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Obtiene un resumen del esquema relevante para una consulta.
        
        Args:
            query: Consulta del usuario
            top_k: Número máximo de tablas a incluir
            
        Returns:
            Diccionario con el resumen del esquema
        """
        relevant_tables = self.search_relevant_tables(query, top_k)
        
        # Crear resumen estructurado
        summary = {
            'query': query,
            'relevant_tables': relevant_tables,
            'total_tables_found': len(relevant_tables),
            'schema_folder': self.schema_folder
        }
        
        return summary
    
    def list_all_tables(self) -> List[str]:
        """
        Lista todas las tablas en el índice de OpenSearch.
        
        Returns:
            Lista de nombres de tablas
        """
        try:
            query_body = {
                "query": {
                    "match_all": {}
                },
                "_source": ["table_name"],
                "size": 1000
            }
            
            response = self.opensearch_client.search(
                index=self.index_name,
                body=query_body,
                request_timeout=5
            )
            
            hits = response['hits']['hits']
            table_names = [hit['_source']['table_name'] for hit in hits]
            
            return table_names
            
        except Exception as e:
            print(f"Error listando tablas: {e}")
            return []
    
    def get_table_content(self, table_name: str) -> str:
        """
        Obtiene el contenido de una tabla específica desde OpenSearch.
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            Contenido de la tabla
        """
        try:
            query_body = {
                "query": {
                    "term": {
                        "table_name": table_name
                    }
                },
                "_source": ["content"],
                "size": 1
            }
            
            response = self.opensearch_client.search(
                index=self.index_name,
                body=query_body,
                request_timeout=3
            )
            
            hits = response['hits']['hits']
            if hits:
                return hits[0]['_source']['content']
            else:
                raise ValueError(f"Tabla '{table_name}' no encontrada en el índice")
                
        except Exception as e:
            print(f"Error obteniendo contenido de tabla {table_name}: {e}")
            raise 