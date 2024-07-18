from unittest.mock import patch

import pytest

from app.core.config import settings
from app.db.redis_db import AsyncRedisConnection


@pytest.fixture
def mock_redis_connection():
    return AsyncRedisConnection()


@pytest.mark.asyncio
async def test_redis_connection_success(mock_redis_connection):
    with patch.object(settings.redis, "host", settings.redis.host), patch.object(
        settings.redis, "port", 6379
    ):
        await mock_redis_connection.connect()
        assert mock_redis_connection.redis is not None
        status = await mock_redis_connection.ping()
        assert status.status == "PONG"


@pytest.mark.asyncio
async def test_redis_write_and_read(mock_redis_connection):
    await mock_redis_connection.connect()
    await mock_redis_connection.write("test_key", "123")
    result = await mock_redis_connection.read("test_key")
    assert result == "123"


@pytest.mark.asyncio
async def test_redis_operations_without_connection(mock_redis_connection):
    with pytest.raises(ConnectionError):
        await mock_redis_connection.write("test_key", "123")

    with pytest.raises(ConnectionError):
        await mock_redis_connection.read("test_key")
