from redis import Redis, RedisError
from core.config import settings


class RedisConnection:
    redisconn = None

    def start_connection(self):
        try:
            self.redisconn = Redis.from_url(settings.redis.redis_db_url)
            self.redisconn.ping()
        except RedisError as e:
            raise ConnectionError("Connection to Redis. Check is Redis is up")
        else:
            print("Connection to Redis is up.")

    def close_connection(self):
        self.redisconn.close()
        print("Connection to Redis is down.")

    def write(self, key: str, value: int):
        self.redisconn.set(key, value)

    def read(self, key: str):
        return self.redisconn.get(key)


redis = RedisConnection()
