from redis import Redis
from utils.config import redis_db_url

class RedisClient:
    def __init__(self):
        self.redis: Redis = None

    async def initialize(self):
        self.redis = Redis.from_url(redis_db_url)
        self.redis.ping()

    async def close(self):
        if self.redis:
            self.redis.close()

redis_client = RedisClient()

async def get_redis():
    return redis_client.redis

async def start_redis(app):
    await redis_client.initialize()

async def stop_redis(app):
    await redis_client.close()
