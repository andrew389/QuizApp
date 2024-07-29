import pytest
from unittest.mock import AsyncMock

from app.schemas.quiz import (
    QuizCreate,
    QuizBase,
)
from app.services.quiz import QuizService
from app.uow.unitofwork import UnitOfWork
from app.exceptions.auth import UnAuthorizedException


@pytest.mark.asyncio
async def test_create_quiz():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.quiz = AsyncMock()
    mock_uow.member = AsyncMock()
    mock_uow.question = AsyncMock()

    quiz_data = QuizCreate(title="Test Quiz", company_id=1, questions=[1, 2])
    mock_uow.question.find_one.return_value = True
    mock_uow.quiz.add_one.return_value = quiz_data

    with pytest.raises(UnAuthorizedException):
        await QuizService.create_quiz(mock_uow, quiz_data, current_user_id=1)


@pytest.mark.asyncio
async def test_delete_quiz():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.quiz = AsyncMock()
    mock_uow.member = AsyncMock()
    mock_uow.question = AsyncMock()

    quiz_id = 1
    mock_uow.quiz.find_one.return_value = QuizBase(
        id=quiz_id, title="Test Quiz", company_id=1
    )

    with pytest.raises(UnAuthorizedException):
        await QuizService.delete_quiz(mock_uow, quiz_id, current_user_id=1)
