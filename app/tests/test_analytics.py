from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from datetime import datetime
from app.services.analytics import AnalyticsService
from app.uow.unitofwork import UnitOfWork
from app.services.member_management import MemberManagement


@pytest.mark.asyncio
async def test_calculate_average_score_within_company():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.answered_question = AsyncMock()
    mock_uow.answered_question.find_by_user_and_company = AsyncMock(
        return_value=[
            MagicMock(is_correct=True),
            MagicMock(is_correct=False),
            MagicMock(is_correct=True),
        ]
    )

    average_score = await AnalyticsService.calculate_average_score_within_company(
        mock_uow, user_id=1, company_id=1
    )

    assert average_score == 0.67


@pytest.mark.asyncio
async def test_calculate_average_score_across_system():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.answered_question = AsyncMock()
    mock_uow.answered_question.find_by_user = AsyncMock(
        return_value=[
            MagicMock(is_correct=True),
            MagicMock(is_correct=False),
            MagicMock(is_correct=True),
        ]
    )

    average_score = await AnalyticsService.calculate_average_score_across_system(
        mock_uow, user_id=1
    )
    assert average_score == 0.67


@pytest.mark.asyncio
async def test_calculate_average_scores_by_quiz():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.answered_question = AsyncMock()
    mock_uow.answered_question.find_by_user_and_date_range = AsyncMock(
        return_value=[
            MagicMock(quiz_id=1, is_correct=True),
            MagicMock(quiz_id=1, is_correct=False),
            MagicMock(quiz_id=2, is_correct=True),
        ]
    )

    average_scores = await AnalyticsService.calculate_average_scores_by_quiz(
        mock_uow,
        user_id=1,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31),
    )
    assert average_scores == {1: 0.5, 2: 1.0}


@pytest.mark.asyncio
async def test_get_last_completion_timestamps():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.answered_question = AsyncMock()
    mock_uow.answered_question.find_by_user = AsyncMock(
        return_value=[
            MagicMock(quiz_id=1, created_at=datetime(2024, 7, 23)),
            MagicMock(quiz_id=1, created_at=datetime(2024, 7, 22)),
            MagicMock(quiz_id=2, created_at=datetime(2024, 7, 21)),
        ]
    )

    last_completion_timestamps = await AnalyticsService.get_last_completion_timestamps(
        mock_uow, user_id=1
    )
    assert last_completion_timestamps == {
        1: datetime(2024, 7, 23),
        2: datetime(2024, 7, 21),
    }


@pytest.mark.asyncio
async def test_calculate_company_members_average_scores():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.member = AsyncMock()
    mock_uow.member.find_one = AsyncMock(return_value=MagicMock(company_id=1))
    mock_uow.member.find_all_by_company_and_role = AsyncMock(
        return_value=[MagicMock(user_id=2), MagicMock(user_id=3)]
    )
    mock_uow.answered_question = AsyncMock()
    mock_uow.answered_question.find_by_user_and_date_range = AsyncMock(
        side_effect=[
            [MagicMock(is_correct=True), MagicMock(is_correct=False)],
            [MagicMock(is_correct=True), MagicMock(is_correct=True)],
        ]
    )

    with patch.object(
        MemberManagement, "check_is_user_have_permission", return_value=True
    ):
        pass


@pytest.mark.asyncio
async def test_list_users_last_quiz_attempts():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.member = AsyncMock()
    mock_uow.member.find_one = AsyncMock(return_value=MagicMock(company_id=1))
    mock_uow.member.find_all_by_company_and_role = AsyncMock(
        return_value=[MagicMock(user_id=2), MagicMock(user_id=3)]
    )
    mock_uow.answered_question = AsyncMock()
    mock_uow.answered_question.find_last_attempt = AsyncMock(
        side_effect=[
            MagicMock(created_at=datetime(2024, 7, 23)),
            MagicMock(created_at=datetime(2024, 7, 22)),
        ]
    )

    with patch.object(
        MemberManagement, "check_is_user_have_permission", return_value=True
    ):
        pass


@pytest.mark.asyncio
async def test_calculate_detailed_average_scores():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.member = AsyncMock()
    mock_uow.member.find_one = AsyncMock(return_value=MagicMock(company_id=1))
    mock_uow.answered_question = AsyncMock()
    mock_uow.answered_question.find_by_user_company_and_date_range = AsyncMock(
        return_value=[
            MagicMock(quiz_id=1, is_correct=True),
            MagicMock(quiz_id=1, is_correct=True),
            MagicMock(quiz_id=2, is_correct=False),
        ]
    )

    with patch.object(
        MemberManagement, "check_is_user_have_permission", return_value=True
    ):
        pass
