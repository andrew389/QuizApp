import pytest
from unittest.mock import AsyncMock, MagicMock
from app.schemas.user import UserCreate, UserDetail, UserUpdate
from app.services.user import UserService
from app.repositories.unitofwork import IUnitOfWork


@pytest.mark.asyncio
async def test_add_user():
    # Arrange
    mock_uow = AsyncMock(IUnitOfWork)
    mock_uow.user = AsyncMock()

    user_data = UserCreate(
        username="testuser", email="test@example.com", hashed_password="password"
    )
    hashed_password = "hashed_password"

    mock_uow.user.add_one.return_value = 1
    mock_uow.user.find_one.return_value = MagicMock(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
    )

    # Act
    user_detail = await UserService.add_user(mock_uow, user_data)

    # Assert
    assert user_detail.username == user_data.username
    assert user_detail.email == user_data.email
    mock_uow.user.add_one.assert_called_once()
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_users():
    # Arrange
    mock_uow = AsyncMock(IUnitOfWork)
    mock_uow.user = AsyncMock()

    mock_users = [MagicMock(id=1, username="testuser", email="test@example.com")]
    mock_uow.user.find_all.return_value = mock_users

    # Act
    users_list = await UserService.get_users(mock_uow)

    # Assert
    assert len(users_list.users) == len(mock_users)
    assert users_list.users[0].username == mock_users[0].username
    assert users_list.users[0].email == mock_users[0].email
    mock_uow.user.find_all.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_by_id():
    # Arrange
    mock_uow = AsyncMock(IUnitOfWork)
    mock_uow.user = AsyncMock()

    user_id = 1
    mock_user = MagicMock(id=user_id, username="testuser", email="test@example.com")
    mock_uow.user.find_one.return_value = mock_user

    # Act
    user_detail = await UserService.get_user_by_id(mock_uow, user_id)

    # Assert
    assert user_detail.id == user_id
    assert user_detail.username == mock_user.username
    assert user_detail.email == mock_user.email
    mock_uow.user.find_one.assert_called_once_with(id=user_id)


@pytest.mark.asyncio
async def test_update_user():
    # Arrange
    mock_uow = AsyncMock(IUnitOfWork)
    mock_uow.user = AsyncMock()

    user_id = 1
    user_update = UserUpdate(
        username="updateduser",
        email="updated@example.com",
        hashed_password="newpassword",
    )
    mock_user = MagicMock(
        id=user_id,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
    )
    updated_user = MagicMock(
        id=user_id,
        username="updateduser",
        email="updated@example.com",
        hashed_password="hashed_password",
    )

    # Modify username and email in mock_user to reflect the updated values
    mock_user.username = user_update.username
    mock_user.email = user_update.email

    mock_uow.user.find_one.return_value = mock_user
    mock_uow.user.edit_one.return_value = updated_user

    # Act
    user_detail = await UserService.update_user(mock_uow, user_id, user_update)

    # Assert
    assert user_detail.id == user_id
    assert user_detail.username == user_update.username
    assert user_detail.email == user_update.email
    mock_uow.user.edit_one.assert_called_once()
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_user():
    # Arrange
    mock_uow = AsyncMock(IUnitOfWork)
    mock_uow.user = AsyncMock()

    user_id = 1
    mock_uow.user.delete_one.return_value = user_id

    # Act
    deleted_user_id = await UserService.delete_user(mock_uow, user_id)

    # Assert
    assert deleted_user_id == user_id
    mock_uow.user.delete_one.assert_called_once_with(user_id)
    mock_uow.commit.assert_called_once()
