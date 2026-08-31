from redis import asyncio as aioredis

from app.config.config import redis_host


def init_redis_pool():
    redis_ins = aioredis.from_url(
        f"redis://{redis_host}", encoding="utf8", decode_responses=True
    )
    return redis_ins


class RedisService:
    def __init__(self) -> None:
        self._redis = init_redis_pool()

    async def get(self, key, expiry=1, set_value=False) -> dict:
        data = await self._redis.get(key)
        if data and set_value:
            await self._redis.set(key, data, ex=expiry)
        return data

    async def set(self, key, value, expiry):
        return await self._redis.set(key, value, ex=expiry)


def init_sync_redis():
    import redis
    conn = redis.from_url(f"redis://{redis_host}")
    return conn
