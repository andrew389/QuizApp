from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User
from app.services.auth import AuthService
from app.uow.unitofwork import IUnitOfWork

client = TestClient(app)


@pytest.mark.asyncio
async def test_login_for_access_token():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_user = User(
        id=1,
        email="test@test.com",
        password="hashedpassword",
        is_active=True,
        is_superuser=False,
    )

    AuthService.authenticate_user = AsyncMock(return_value=mock_user)
    AuthService.create_access_token = MagicMock(return_value="mock_access_token")

    response = client.post(
        "api/v1/me/login", data={"email": "test@test.com", "password": "password"}
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_read_users_me():
    mock_user = User(
        id=1,
        email="test@test.com",
        password="hashedpassword",
        is_active=True,
        is_superuser=False,
    )

    AuthService.get_current_user = AsyncMock(return_value=mock_user)

    response = client.get("api/v1/me/", headers={"Authorization": "Bearer mock_token"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_incorrect_login():
    mock_uow = AsyncMock(IUnitOfWork)
    AuthService.authenticate_user = AsyncMock(return_value=None)

    response = client.post(
        "api/v1/me/login", data={"email": "wronguser", "password": "wrongpassword"}
    )

    assert response.status_code == 422
