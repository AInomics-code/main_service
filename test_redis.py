import redis
import boto3
from botocore.config import Config
import socket

REDIS_ENDPOINT = 'localhost'

def test_redis_connection():
    try:
        # Create Redis client with local configuration
        redis_client = redis.Redis(
            host=REDIS_ENDPOINT,
            port=6379,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        # Test connection with a simple ping
        print("Intentando conectar a Redis...")
        response = redis_client.ping()
        print("Conexión exitosa a Redis!")
        print(f"Respuesta del ping: {response}")
        
        # Test simple set and get
        redis_client.set('test_key', 'Hello Redis!')
        value = redis_client.get('test_key')
        print(f"Valor recuperado: {value.decode('utf-8')}")
        
    except redis.exceptions.ConnectionError as e:
        print(f"Error de conexión: {str(e)}")
        print("\nVerificando si el endpoint es accesible...")
        try:
            socket.create_connection((REDIS_ENDPOINT, 6379), timeout=5)
            print("El puerto está abierto pero Redis no responde")
        except socket.error as se:
            print(f"No se puede acceder al endpoint: {str(se)}")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")

if __name__ == "__main__":
    test_redis_connection()
