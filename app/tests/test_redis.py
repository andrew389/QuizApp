import pytest
from unittest.mock import patch, MagicMock
from redis import RedisError
from db.redis_db import RedisConnection


@pytest.fixture
def redis():
    redis_instance = RedisConnection()
    redis_instance.start_connection()
    yield redis_instance
    redis_instance.close_connection()


@pytest.mark.asyncio
async def test_redis_write(redis):
    key = "test_key"
    value = 123
    redis.write(key, value)
    assert int(redis.read(key)) == value


@pytest.mark.asyncio
async def test_redis_read(redis):
    key = "test_key"
    value = 123
    redis.write(key, value)
    assert int(redis.read(key)) == value


@pytest.mark.asyncio
async def test_redis_connection_error():
    with patch("redis.Redis.from_url", side_effect=ConnectionError):
        redis = RedisConnection()
        with pytest.raises(ConnectionError):
            redis.start_connection()


@pytest.mark.asyncio
async def test_redis_ping_error():
    mock_redis = MagicMock()
    mock_redis.ping.side_effect = RedisError("Mocked Redis Error")
    with patch("redis.Redis.from_url", return_value=mock_redis):
        redis = RedisConnection()
        with pytest.raises(ConnectionError):
            redis.start_connection()
