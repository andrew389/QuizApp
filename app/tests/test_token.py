import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.services.auth import auth_service
from app.models.user import User
from app.repositories.unitofwork import IUnitOfWork

client = TestClient(app)


@pytest.mark.asyncio
async def test_login_for_access_token():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_user = User(
        id=1,
        username="testuser",
        email="test@test.com",
        hashed_password="hashedpassword",
        is_active=True,
        is_superuser=False,
    )

    auth_service.authenticate_user = AsyncMock(return_value=mock_user)
    auth_service.create_access_token = MagicMock(return_value="mock_access_token")

    response = client.post(
        "api/v1/auth/token", data={"username": "testuser", "password": "password"}
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_read_users_me():
    mock_user = User(
        id=1,
        username="testuser",
        email="test@test.com",
        hashed_password="hashedpassword",
        is_active=True,
        is_superuser=False,
    )

    auth_service.get_current_user = AsyncMock(return_value=mock_user)

    response = client.get(
        "api/v1/auth/me", headers={"Authorization": "Bearer mock_token"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_incorrect_login():
    mock_uow = AsyncMock(IUnitOfWork)
    auth_service.authenticate_user = AsyncMock(return_value=None)

    response = client.post(
        "api/v1/auth/token", data={"username": "wronguser", "password": "wrongpassword"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
