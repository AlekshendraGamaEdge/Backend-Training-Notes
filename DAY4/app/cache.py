import logging
import redis
import json
from typing import Optional

logger = logging.getLogger(__name__)


try:
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    redis_client.ping() 
    logger.info("Connected to Redis successfully")
except redis.ConnectionError:
    logger.error("Redis not available. Caching will be disabled.")
    redis_client = None

def cache_get(key: str) -> Optional[dict]:
    if redis_client is None:
        return None
    value = redis_client.get(key)
    if value:
        logger.info(f"Cache HIT for key '{key}'")
        return json.loads(value)
    logger.info(f"Cache MISS for key '{key}'")
    return None

def cache_set(key: str, value: dict, ttl_seconds: int = 30):
    if redis_client is None:
        return
    redis_client.setex(key, ttl_seconds, json.dumps(value))
    logger.info(f"Cached key '{key}' with TTL {ttl_seconds}s")

def cache_delete(key: str):
    if redis_client is None:
        return
    redis_client.delete(key)
    logger.info(f"Invalidated cache key '{key}'")