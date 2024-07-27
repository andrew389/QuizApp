from unittest.mock import AsyncMock, MagicMock
import pytest
from fastapi import Request
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException, UpdatingException
from app.schemas.notification import (
    NotificationCreate,
    NotificationBase,
)
from app.services.notification import NotificationService
from app.uow.unitofwork import IUnitOfWork


@pytest.mark.asyncio
async def test_send_notifications():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_member_repo = AsyncMock()
    mock_notification_repo = AsyncMock()

    mock_uow.member = mock_member_repo
    mock_uow.notification = mock_notification_repo

    company_id = 1
    message = "Test Notification"
    members = [MagicMock(user_id=1), MagicMock(user_id=2)]
    mock_member_repo.find_all_by_company_and_role.return_value = members

    await NotificationService.send_notifications(mock_uow, company_id, message)

    notifications = [
        NotificationCreate(
            message=message,
            receiver_id=member.user_id,
            company_id=company_id,
            status="pending",
        )
        for member in members
    ]

    for notification in notifications:
        mock_notification_repo.add_one.assert_any_call(
            notification.dict(exclude={"id"})
        )


@pytest.mark.asyncio
async def test_mark_as_read_success():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_notification_repo = AsyncMock()

    notification_id = 1
    user_id = 1
    mock_notification = MagicMock(
        id=notification_id, receiver_id=user_id, status="pending"
    )
    mock_uow.notification = mock_notification_repo
    mock_notification_repo.find_one.return_value = mock_notification

    await NotificationService.mark_as_read(mock_uow, user_id, notification_id)

    mock_notification_repo.edit_one.assert_called_once_with(
        notification_id, {"status": "read"}
    )


@pytest.mark.asyncio
async def test_mark_as_read_unauthorized():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_notification_repo = AsyncMock()

    notification_id = 1
    user_id = 2
    mock_notification = MagicMock(id=notification_id, receiver_id=1, status="pending")
    mock_uow.notification = mock_notification_repo
    mock_notification_repo.find_one.return_value = mock_notification

    with pytest.raises(UnAuthorizedException):
        await NotificationService.mark_as_read(mock_uow, user_id, notification_id)

    mock_notification_repo.edit_one.assert_not_called()
    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_mark_as_read_already_read():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_notification_repo = AsyncMock()

    notification_id = 1
    user_id = 1
    mock_notification = MagicMock(
        id=notification_id, receiver_id=user_id, status="read"
    )
    mock_uow.notification = mock_notification_repo
    mock_notification_repo.find_one.return_value = mock_notification

    with pytest.raises(UpdatingException):
        await NotificationService.mark_as_read(mock_uow, user_id, notification_id)

    mock_notification_repo.edit_one.assert_not_called()
    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_get_notifications():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_notification_repo = AsyncMock()

    mock_uow.notification = mock_notification_repo

    user_id = 1
    skip = 0
    limit = 10
    request = MagicMock(Request)

    # Creating mock notifications with required fields
    mock_notifications = [
        NotificationBase(
            id=1,
            message="Test notification",
            receiver_id=user_id,
            company_id=1,
            status="pending",
        ),
        NotificationBase(
            id=2,
            message="Another notification",
            receiver_id=user_id,
            company_id=1,
            status="pending",
        ),
    ]
    mock_notification_repo.find_all_by_receiver.return_value = mock_notifications

    with pytest.raises(TypeError):
        await NotificationService.get_notifications(
            mock_uow, request, user_id, skip, limit
        )


@pytest.mark.asyncio
async def test_get_notification_by_id_success():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_notification_repo = AsyncMock()

    mock_uow.notification = mock_notification_repo

    notification_id = 1
    user_id = 1
    mock_notification = MagicMock(id=notification_id, receiver_id=user_id)
    mock_notification_repo.find_one.return_value = mock_notification

    response = await NotificationService.get_notification_by_id(
        mock_uow, user_id, notification_id
    )

    assert response.id == notification_id
    mock_notification_repo.find_one.assert_called_once_with(
        id=notification_id, receiver_id=user_id
    )


@pytest.mark.asyncio
async def test_get_notification_by_id_not_found():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_notification_repo = AsyncMock()

    mock_uow.notification = mock_notification_repo

    notification_id = 1
    user_id = 1
    mock_notification_repo.find_one.return_value = None

    with pytest.raises(NotFoundException):
        await NotificationService.get_notification_by_id(
            mock_uow, user_id, notification_id
        )

    mock_notification_repo.find_one.assert_called_once_with(
        id=notification_id, receiver_id=user_id
    )
