import os
import redis.asyncio as redis

redis_client = None

async def init_redis():
    global redis_client
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    redis_client = redis.from_url(redis_url, encoding="utf8", decode_responses=True)

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()

def get_redis_client() -> redis.Redis:
    return redis_client
