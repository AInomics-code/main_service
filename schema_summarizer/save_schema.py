import os
import sys
import logging
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# Agregar el directorio padre al path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDBUpdater:
    def __init__(self):
        self.opensearch_endpoint = settings.OPENSEARCH_ENDPOINT
        self.index_name = "tables"
        self.collection_name = "la-dona-vdb"
        
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
        """Obtener embeddings usando Titan v1"""
        try:
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

    def create_index_if_not_exists(self):
        """Crear el índice si no existe"""
        try:
            if not self.opensearch_client.indices.exists(index=self.index_name):
                index_mapping = {
                    "mappings": {
                        "properties": {
                            "embeddings": {
                                "type": "knn_vector",
                                "dimension": 1536,
                                "method": {
                                    "name": "hnsw",
                                    "space_type": "dotproduct",
                                    "engine": "faiss",
                                    "parameters": {
                                        "ef_construction": 128,
                                        "m": 16
                                    }
                                }
                            },
                            "content": {
                                "type": "text"
                            },
                            "table_name": {
                                "type": "keyword"
                            }
                        }
                    },
                    "settings": {
                        "index": {
                            "knn": True,
                            "knn.algo_param.ef_search": 100
                        }
                    }
                }
                self.opensearch_client.indices.create(index=self.index_name, body=index_mapping)
                logger.info(f"Índice {self.index_name} creado exitosamente")
            else:
                logger.info(f"Índice {self.index_name} ya existe")
        except Exception as e:
            logger.error(f"Error creando índice: {e}")
            raise

    def update_vector_db(self, schema_files_dir):
        """Actualizar la vector database con los archivos de schema"""
        try:
            if not os.path.exists(schema_files_dir):
                logger.error(f"Directorio {schema_files_dir} no existe")
                return

            files = [f for f in os.listdir(schema_files_dir) if f.endswith('.txt')]
            logger.info(f"Encontrados {len(files)} archivos para procesar")

            for filename in files:
                file_path = os.path.join(schema_files_dir, filename)
                table_name = os.path.splitext(filename)[0]  # Nombre sin extensión
                
                logger.info(f"Procesando archivo: {filename}")
                
                # Leer contenido del archivo
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Obtener embeddings
                embeddings = self.get_embeddings(content)
                
                # Preparar documento para indexar
                document = {
                    "embeddings": embeddings,
                    "content": content,
                    "table_name": table_name
                }
                
                # Buscar si ya existe un documento con el mismo table_name
                search_query = {
                    "query": {
                        "term": {
                            "table_name": table_name
                        }
                    }
                }
                
                search_result = self.opensearch_client.search(
                    index=self.index_name,
                    body=search_query,
                    size=1
                )
                
                if search_result['hits']['total']['value'] > 0:
                    # Documento existe, actualizar
                    doc_id = search_result['hits']['hits'][0]['_id']
                    self.opensearch_client.update(
                        index=self.index_name,
                        id=doc_id,
                        body={"doc": document}
                    )
                    logger.info(f"Documento {table_name} actualizado exitosamente")
                else:
                    # Documento no existe, crear nuevo
                    self.opensearch_client.index(
                        index=self.index_name,
                        body=document
                    )
                    logger.info(f"Documento {table_name} creado exitosamente")
            
            # Hacer refresh del índice
            try:
                self.opensearch_client.indices.refresh(index=self.index_name)
                logger.info("Refresh del índice completado")
            except Exception as e:
                logger.warning(f"No se pudo hacer refresh del índice: {e}")
            
            logger.info("Vector database actualizada exitosamente")
            
        except Exception as e:
            logger.error(f"Error actualizando vector database: {e}")
            raise

if __name__ == "__main__":
    updater = VectorDBUpdater()
    # Crear el índice si no existe
    updater.create_index_if_not_exists()
    # Actualizar la vector database con los archivos de schema_files
    updater.update_vector_db(os.path.join(os.path.dirname(__file__), "schema_files"))
