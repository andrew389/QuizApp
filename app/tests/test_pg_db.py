import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from core.config import settings
from db.pg_db import get_async_session
from main import app

test_engine = create_async_engine(settings.postgres_db_test_async_url, echo=True)
test_session = AsyncSession(test_engine)


@pytest.fixture
def test_app() -> FastAPI:
    return app


@pytest.fixture
async def override_get_async_session() -> AsyncSession:
    async with test_session() as session:
        yield session


@pytest.fixture
async def async_client(test_app: FastAPI) -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_ping_db(override_get_async_session: AsyncSession):
    app.dependency_overrides[get_async_session] = lambda: override_get_async_session

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/db")

        assert response.status_code == 200

    app.dependency_overrides.clear()
