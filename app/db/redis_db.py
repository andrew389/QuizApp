import asyncio_redis

from app.core.config import settings
from app.core.logger import logger


class AsyncRedisConnection:
    def __init__(self):
        self.redis = None

    async def connect(self):
        try:
            self.redis = await asyncio_redis.Connection.create(
                host=settings.redis.host, port=int(settings.redis.port)
            )
            await self.redis.ping()
        except ConnectionError as e:
            logger.error("Connection to Redis failed: %s", e)
            raise ConnectionError("Connection to Redis failed") from e
        else:
            logger.info("Connected to Redis.")

    async def disconnect(self):
        if self.redis:
            self.redis.close()
            logger.info("Disconnected from Redis.")

    async def write(self, key: str, value: int):
        if self.redis:
            await self.redis.set(key, value)
        else:
            raise ConnectionError("Redis connection is not established.")

    async def read(self, key: str):
        if self.redis:
            return await self.redis.get(key)
        else:
            raise ConnectionError("Redis connection is not established.")

    async def ping(self):
        if self.redis:
            return await self.redis.ping()
        else:
            raise ConnectionError("Redis connection is not established.")


redis = AsyncRedisConnection()
