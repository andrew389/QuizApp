import datetime
import pytest
from unittest.mock import AsyncMock, patch
from app.services.data_export import DataExportService
from app.services.notification import NotificationService
from app.uow.unitofwork import UnitOfWork
from app.core.tasks import notification_task, send_notification


@pytest.mark.asyncio
async def test_send_notification():
    mock_uow = AsyncMock(UnitOfWork)
    mock_notification_service = AsyncMock(NotificationService)
    mock_uow.__aenter__.return_value = mock_uow

    user_id = 1
    quiz_id = 2
    company_id = 3
    message = "You didn't complete available quiz: 2. Please complete it in next 24h!"

    with patch(
        "app.services.notification.NotificationService.send_one_notification",
        mock_notification_service.send_one_notification,
    ):
        await send_notification(mock_uow, user_id, quiz_id, company_id)


@pytest.mark.asyncio
async def test_notification_task():
    mock_uow = AsyncMock(UnitOfWork)
    mock_data_export_service = AsyncMock(DataExportService)
    mock_uow.__aenter__.return_value = mock_uow

    current_time = datetime.datetime.now()
    cutoff_time = current_time - datetime.timedelta(days=1)

    # Mocking company, member, and quiz data
    mock_company = AsyncMock(id=1)
    mock_user = AsyncMock(user_id=1)
    mock_quiz = AsyncMock(id=1)

    mock_data_export_service.fetch_data.return_value = []

    with patch(
        "app.services.data_export.DataExportService.fetch_data",
        mock_data_export_service.fetch_data,
    ), patch("app.core.tasks.send_notification") as mock_send_notification:
        await notification_task()

        # Check that send_notification was called with the correct parameters

        # Check that fetch_data was called with the correct pattern
        pattern = f"answered_quiz_{mock_user.user_id}_{mock_company.id}_{mock_quiz.id}"
