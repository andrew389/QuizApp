from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import Request

from app.schemas.user import UserCreate, UserUpdate
from app.services.data_export import DataExportService
from app.services.notification import NotificationService
from app.uow.unitofwork import UnitOfWork


@pytest.fixture
def mock_uow():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.answered_question = AsyncMock()
    mock_uow.question = AsyncMock()
    mock_uow.answer = AsyncMock()
    mock_uow.quiz = AsyncMock()
    mock_uow.member = AsyncMock()
    mock_uow.invitation = AsyncMock()
    mock_uow.company = AsyncMock()
    mock_uow.notification = AsyncMock()
    mock_uow.user = AsyncMock()

    setattr(mock_uow, "member", AsyncMock())

    return mock_uow


@pytest.fixture
def mock_company_repo(mock_uow):
    repo = AsyncMock()
    mock_uow.company = repo
    return repo


@pytest.fixture
def mock_member_repo(mock_uow):
    repo = AsyncMock()
    mock_uow.member = repo
    return repo


@pytest.fixture
def mock_user_repo(mock_uow):
    repo = AsyncMock()
    mock_uow.user = repo
    return repo


@pytest.fixture
def mock_notification_repo(mock_uow):
    repo = AsyncMock()
    mock_uow.notification = repo
    return repo


@pytest.fixture
def mock_request():
    return MagicMock(Request)


@pytest.fixture
def mock_data_export_service():
    return AsyncMock(DataExportService)


@pytest.fixture
def mock_notification_service():
    return AsyncMock(NotificationService)


@pytest.fixture
def mock_redis():
    with patch("app.services.data_export.redis_connection.redis") as mock_redis:
        mock_redis.keys = AsyncMock()
        mock_redis.get = AsyncMock()
        yield mock_redis


@pytest.fixture
def mock_member_management():
    with patch("app.services.data_export.MemberManagement") as mock_member_management:
        mock_member_management.check_is_user_have_permission = AsyncMock()
        yield mock_member_management


@pytest.fixture
def user_data():
    return UserCreate(
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


@pytest.fixture
def user_update():
    return UserUpdate(
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


@pytest.fixture
def mock_user(user_data):
    return MagicMock(**user_data.dict(), id=1)


@pytest.fixture
def updated_user(user_update):
    return MagicMock(**user_update.dict(), id=1)


@pytest.fixture
def mock_user_detail(mock_user):
    return mock_user
