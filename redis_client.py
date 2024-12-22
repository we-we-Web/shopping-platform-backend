import redis.asyncio as redis
from loguru import logger
import os
from dotenv import load_dotenv

redis_client = None

load_dotenv()

async def init_redis():
    global redis_client
    logger.info("Initializing Redis client...")
    redis_url = os.getenv("REDIS_URL")
    redis_client = redis.from_url(redis_url, decode_responses=True)

async def close_redis():
    global redis_client
    if redis_client:
        logger.info("Closing Redis connection...")
        await redis_client.close()

async def set_value(key: str, value: str, expire: int = 3600):
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized")
    await redis_client.set(key, value, ex=expire)

async def get_value(key: str) -> str:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized")
    return await redis_client.get(key)
