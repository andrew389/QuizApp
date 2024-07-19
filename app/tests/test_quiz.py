import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from app.schemas.quiz import (
    QuizCreate,
    QuizUpdate,
    QuizBase,
    QuizResponse,
    QuizzesListResponse,
)
from app.services.quiz import QuizService
from app.uow.unitofwork import UnitOfWork
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException


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
async def test_get_quizzes():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.quiz = AsyncMock()
    mock_uow.member = AsyncMock()

    company_id = 1
    mock_quizzes = [QuizBase(id=1, title="Test Quiz", company_id=1)]
    mock_uow.quiz.find_all.return_value = mock_quizzes

    with pytest.raises(UnAuthorizedException):
        await QuizService.get_quizzes(mock_uow, company_id, current_user_id=1)


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
