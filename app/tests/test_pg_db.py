import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings
from app.db.pg_db import get_async_session


@pytest.fixture(scope="module")
def mock_async_session():
    engine = create_async_engine(settings.database.test_async_url)
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    return async_session_maker


@pytest.mark.asyncio
async def test_get_async_session(mock_async_session):
    async with mock_async_session() as session:
        async for _ in get_async_session():
            assert isinstance(session, AsyncSession)
