from unittest.mock import MagicMock

import pytest
from app.exceptions.auth import UnAuthorizedException
from app.services.user import UserService


@pytest.mark.asyncio
async def test_add_user(mock_uow, mock_user_repo, user_data):
    mock_user_repo.find_one.return_value = True

    with pytest.raises(ValueError):
        await UserService.add_user(mock_uow, user_data)

    mock_user_repo.add_one.assert_not_called()
    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_get_users(mock_uow, mock_request):
    mock_users = [
        MagicMock(id=1, email="test@example.com", firstname="John", lastname="Doe")
    ]
    mock_uow.user.find_all.return_value = mock_users

    with pytest.raises(TypeError):
        await UserService.get_users(mock_uow, mock_request)


@pytest.mark.asyncio
async def test_get_user_by_id(mock_uow, mock_user):
    mock_uow.user.find_one.return_value = mock_user

    user_detail = await UserService.get_user_by_id(mock_uow, mock_user.id)

    assert user_detail.id == mock_user.id
    assert user_detail.email == mock_user.email
    mock_uow.user.find_one.assert_called_once_with(id=mock_user.id)


@pytest.mark.asyncio
async def test_update_user(mock_uow, mock_user, user_update, updated_user):
    mock_uow.user.find_one.return_value = mock_user
    mock_uow.user.edit_one.return_value = updated_user

    user_detail = await UserService.update_user(mock_uow, mock_user.id, 1, user_update)

    assert user_detail.id == mock_user.id
    mock_uow.user.edit_one.assert_called_once()


@pytest.mark.asyncio
async def test_deactivate_user(mock_uow, mock_user):
    mock_user.is_active = True
    mock_uow.user.find_one.return_value = mock_user
    mock_uow.user.edit_one.return_value = mock_user

    deactivated_user = await UserService.deactivate_user(mock_uow, mock_user.id, 1)

    assert not deactivated_user.is_active
    mock_uow.user.edit_one.assert_called_once_with(mock_user.id, {"is_active": False})


@pytest.mark.asyncio
async def test_failure_update_user(mock_uow, mock_user, user_update):
    mock_user.id = 12
    updated_user = MagicMock(
        id=13, firstname=user_update.firstname, lastname=user_update.lastname
    )
    mock_uow.user.find_one.return_value = mock_user
    mock_uow.user.edit_one.return_value = updated_user

    with pytest.raises(UnAuthorizedException):
        await UserService.update_user(mock_uow, 1, 2, user_update)
