from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions.auth import UnAuthorizedException
from app.schemas.user import UserCreate, UserUpdate
from app.services.user import UserService
from app.uow.unitofwork import IUnitOfWork


@pytest.mark.asyncio
async def test_add_user():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_user_repo = AsyncMock()

    mock_uow.user = mock_user_repo

    user_data = UserCreate(
        email="test@test.com",
        password="password",
        firstname="John",
        lastname="Doe",
        city="New York",
        phone="1234567890",
        avatar="default.jpg",
        created_at="2024-07-09 09:40:59.493975",
        updated_at="2024-07-09 09:40:59.493975",
        is_active=True,
        is_superuser=False,
    )
    mock_user_repo.find_one.return_value = True

    with pytest.raises(ValueError):
        await UserService.add_user(mock_uow, user_data)

    mock_user_repo.add_one.assert_not_called()
    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_get_users():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_uow.user = AsyncMock()

    mock_users = [
        MagicMock(
            id=1,
            email="test@example.com",
            password="password",
            firstname="John",
            lastname="Doe",
            city="New York",
            phone="1234567890",
            avatar="default.jpg",
            created_at="2024-07-09 09:40:59.493975",
            updated_at="2024-07-09 09:40:59.493975",
            is_active=True,
            is_superuser=False,
        )
    ]
    mock_uow.user.find_all.return_value = mock_users

    users_list = await UserService.get_users(mock_uow)

    assert len(users_list.users) == len(mock_users)
    assert users_list.users[0].email == mock_users[0].email
    mock_uow.user.find_all.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_by_id():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_uow.user = AsyncMock()

    user_id = 1
    mock_user = MagicMock(
        id=user_id,
        email="test@example.com",
        password="password",
        firstname="John",
        lastname="Doe",
        city="New York",
        phone="1234567890",
        avatar="default.jpg",
        created_at="2024-07-09 09:40:59.493975",
        updated_at="2024-07-09 09:40:59.493975",
        is_active=True,
        is_superuser=False,
    )
    mock_uow.user.find_one.return_value = mock_user

    user_detail = await UserService.get_user_by_id(mock_uow, user_id)

    assert user_detail.id == user_id
    assert user_detail.email == mock_user.email
    mock_uow.user.find_one.assert_called_once_with(id=user_id)


@pytest.mark.asyncio
async def test_update_user():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_uow.user = AsyncMock()

    user_id = 1
    user_update = UserUpdate(
        email="updated@example.com",
        firstname="John",
        lastname="Doe",
        city="New York",
        phone="1234567890",
        avatar="default.jpg",
        created_at="2024-07-09 09:40:59.493975",
        updated_at="2024-07-09 09:40:59.493975",
        is_active=True,
        is_superuser=False,
    )
    mock_user = MagicMock(
        id=user_id,
        email="test@example.com",
        password="password",
        firstname="John",
        lastname="Doe",
        city="New York",
        phone="1234567890",
        avatar="default.jpg",
        created_at="2024-07-09 09:40:59.493975",
        updated_at="2024-07-09 09:40:59.493975",
        is_active=True,
        is_superuser=False,
    )
    updated_user = MagicMock(
        id=user_id,
        email="updated@example.com",
        password="password",
        firstname="John",
        lastname="Doe",
        city="New York",
        phone="1234567890",
        avatar="default.jpg",
        created_at="2024-07-09 09:40:59.493975",
        updated_at="2024-07-09 09:40:59.493975",
        is_active=True,
        is_superuser=False,
    )

    mock_uow.user.find_one.return_value = mock_user
    mock_uow.user.edit_one.return_value = updated_user

    user_detail = await UserService.update_user(mock_uow, user_id, 1, user_update)

    assert user_detail.id == user_id
    mock_uow.user.edit_one.assert_called_once()


@pytest.mark.asyncio
async def test_deactivate_user():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_uow.user = AsyncMock()

    user_id = 1
    mock_user = MagicMock(
        id=user_id,
        email="test@example.com",
        password="password",
        firstname="John",
        lastname="Doe",
        city="New York",
        phone="1234567890",
        avatar="default.jpg",
        created_at="2024-07-09 09:40:59.493975",
        updated_at="2024-07-09 09:40:59.493975",
        is_active=False,
        is_superuser=False,
    )
    mock_uow.user.find_one.return_value = mock_user
    mock_uow.user.edit_one.return_value = mock_user

    deactivated_user = await UserService.deactivate_user(mock_uow, user_id, 1)

    assert deactivated_user.is_active == False
    mock_uow.user.edit_one.assert_called_once_with(user_id, {"is_active": False})


@pytest.mark.asyncio
async def test_failure_update_user():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_uow.user = AsyncMock()

    user_id = 1
    user_update = UserUpdate(
        email="updated@example.com",
        firstname="John",
        lastname="Doe",
        city="New York",
        phone="1234567890",
        avatar="default.jpg",
        created_at="2024-07-09 09:40:59.493975",
        updated_at="2024-07-09 09:40:59.493975",
        is_active=True,
        is_superuser=False,
    )
    mock_user = MagicMock(
        id=12,
        email="test@example.com",
        password="password",
        firstname="John",
        lastname="Doe",
        city="New York",
        phone="1234567890",
        avatar="default.jpg",
        created_at="2024-07-09 09:40:59.493975",
        updated_at="2024-07-09 09:40:59.493975",
        is_active=True,
        is_superuser=False,
    )
    updated_user = MagicMock(
        id=13,
        email="updated@example.com",
        password="password",
        firstname="John",
        lastname="Doe",
        city="New York",
        phone="1234567890",
        avatar="default.jpg",
        created_at="2024-07-09 09:40:59.493975",
        updated_at="2024-07-09 09:40:59.493975",
        is_active=True,
        is_superuser=False,
    )

    mock_uow.user.find_one.return_value = mock_user
    mock_uow.user.edit_one.return_value = updated_user

    with pytest.raises(UnAuthorizedException):
        await UserService.update_user(mock_uow, user_id, 2, user_update)
