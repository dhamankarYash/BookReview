# cache.py

import redis
import logging

logger = logging.getLogger(__name__)

try:
    # Create a Redis client connection
    redis_client = redis.Redis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True  # ensures you get strings instead of bytes
    )

    # Test the connection
    redis_client.ping()
    logging.info("✅ Connected to Redis")

except redis.exceptions.ConnectionError:
    redis_client = None
    logging.warning("⚠️ Redis connection failed - running without cache")
