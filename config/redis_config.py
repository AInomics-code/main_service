"""
Redis configuration for the AI service
"""
import redis

# Redis connection settings
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'decode_responses': True,
    'socket_timeout': 5,
    'socket_connect_timeout': 5,
    'retry_on_timeout': True,
    'health_check_interval': 30
}

def get_redis_client():
    """
    Get a Redis client instance with the configured settings
    """
    return redis.Redis(**REDIS_CONFIG) 