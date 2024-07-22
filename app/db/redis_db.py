import asyncio_redis
from app.core.config import settings
from app.core.logger import logger


class AsyncRedisConnection:
    """
    Handles asynchronous connections to a Redis database using asyncio_redis.

    Attributes:
        redis: The Redis connection instance.
    """

    def __init__(self):
        """
        Initializes the AsyncRedisConnection instance.
        """
        self.redis = None

    async def connect(self):
        """
        Establishes a connection to the Redis database.

        Raises:
            ConnectionError: If the connection to Redis fails.
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
        Closes the connection to the Redis database.

        If there is no active connection, this method does nothing.
        """
        if self.redis:
            self.redis.close()
            logger.info("Disconnected from Redis.")

    async def write(self, key: str, value: int):
        """
        Writes a value to Redis with the specified key.

        Args:
            key (str): The key under which the value will be stored.
            value (int): The value to be stored in Redis.

        Raises:
            ConnectionError: If the Redis connection is not established.
        """
        if self.redis:
            await self.redis.set(key, value)
        else:
            raise ConnectionError("Redis connection is not established.")

    async def read(self, key: str):
        """
        Reads a value from Redis using the specified key.

        Args:
            key (str): The key of the value to be retrieved.

        Returns:
            The value associated with the specified key.

        Raises:
            ConnectionError: If the Redis connection is not established.
        """
        if self.redis:
            return await self.redis.get(key)
        else:
            raise ConnectionError("Redis connection is not established.")

    async def ping(self):
        """
        Pings the Redis server to check if it is responsive.

        Returns:
            The response from the Redis server.

        Raises:
            ConnectionError: If the Redis connection is not established.
        """
        if self.redis:
            return await self.redis.ping()
        else:
            raise ConnectionError("Redis connection is not established.")


# Instantiate the Redis connection object
redis = AsyncRedisConnection()
