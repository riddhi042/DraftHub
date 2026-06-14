# backend/app/db/redis_client.py
import redis
from app.core.settings import get_settings

settings = get_settings()

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True,
)


def get_redis():
    return redis_client