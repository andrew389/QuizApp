from typing import Optional, List

import asyncio_redis

from app.core.config import settings
from app.core.logger import logger


class AsyncRedisConnection:
    def __init__(self):
        self.redis = None

    async def connect(self):
        """
        Connects to the Redis server and checks the connection.
        """
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
        """
        Closes the connection to the Redis server.
        """
        if self.redis:
            self.redis.close()
            logger.info("Disconnected from Redis.")

    async def write(self, key: str, value: int):
        """
        Writes a value to Redis with the specified key.

        Args:
            key (str): The key under which to store the value.
            value (int): The value to store.
        """
        if self.redis:
            await self.redis.set(key, value)
        else:
            raise ConnectionError("Redis connection is not established.")

    async def write_with_ttl(self, key: str, value: int, ttl: int):
        """
        Write a value to Redis with a specified time-to-live (TTL).

        Args:
            key (str): The key under which the value is stored.
            value (int): The value to store.
            ttl (int): The time-to-live in seconds for the stored value.
        """
        if self.redis:
            await self.redis.set(key, value)
            await self.redis.expire(key, ttl)
            logger.info(f"The data was saved in redis")
        else:
            raise ConnectionError("Redis connection is not established.")

    async def read(self, key: str):
        """
        Reads a value from Redis with the specified key.

        Args:
            key (str): The key to read the value for.

        Returns:
            The value stored in Redis.
        """
        if self.redis:
            return await self.redis.get(key)
        else:
            raise ConnectionError("Redis connection is not established.")

    async def read_by_filters(
        self,
        user_id: Optional[int] = None,
        company_id: Optional[int] = None,
        quiz_id: Optional[int] = None,
    ) -> List[str]:
        if not self.redis:
            raise ConnectionError("Redis connection is not established.")

        keys = []
        if user_id:
            if company_id:
                if quiz_id:
                    keys.append(
                        f"user_id:{user_id}:company_id:{company_id}:quiz_id:{quiz_id}"
                    )
                else:
                    keys.append(f"user_id:{user_id}:company_id:{company_id}")
            else:
                keys.append(f"user_id:{user_id}")
        elif company_id:
            if quiz_id:
                keys.append(f"company_id:{company_id}:quiz_id:{quiz_id}")
            else:
                keys.append(f"company_id:{company_id}")
        elif quiz_id:
            keys.append(f"quiz_id:{quiz_id}")

        data = []
        for key in keys:
            value = await self.redis.get(key)
            if value:
                data.append(value)
        return data

    async def ping(self):
        """
        Sends a ping to the Redis server to check if the connection is alive.

        Returns:
            The result of the ping operation.
        """
        if self.redis:
            return await self.redis.ping()
        else:
            raise ConnectionError("Redis connection is not established.")


redis = AsyncRedisConnection()
