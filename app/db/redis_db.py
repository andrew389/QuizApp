import aioredis
import asyncio
import ssl
from app.core.config import settings
from app.core.logger import logger


class AsyncRedisConnection:
    def __init__(self):
        self.redis = None

    async def connect(self):
        """
        Connects to the Redis server with TLS encryption and checks the connection.
        """
        try:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            self.redis = await aioredis.from_url(
                f"rediss://{settings.redis.host}:{settings.redis.port}",
                password=settings.redis.password,
                ssl=ssl_context,
            )
            await self.redis.ping()
        except aioredis.RedisError as e:
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
            await self.redis.wait_closed()
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
            logger.info("The data was saved in redis")
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


redis_connection = AsyncRedisConnection()
