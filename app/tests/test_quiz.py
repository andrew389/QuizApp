import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import Request
from pydantic import ValidationError

from app.schemas.question import QuestionResponse
from app.schemas.quiz import (
    QuizCreate,
    QuizBase,
    QuizUpdate,
)
from app.services.quiz import QuizService
from app.uow.unitofwork import UnitOfWork
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException, FetchingException


@pytest.mark.asyncio
async def test_create_quiz_success(mock_uow):
    quiz_data = QuizCreate(title="Test Quiz", company_id=1, questions=[1, 2])
    mock_uow.member.check_is_user_have_permission.return_value = True
    mock_uow.question.find_one.return_value = True
    mock_uow.quiz.add_one.return_value = quiz_data

    with pytest.raises(UnAuthorizedException):
        await QuizService.create_quiz(mock_uow, quiz_data, current_user_id=1)


@pytest.mark.asyncio
async def test_update_quiz_success(mock_uow):
    quiz_id = 1
    quiz_update = QuizUpdate(title="Updated Quiz", description="Updated Description")
    mock_uow.quiz.find_one.return_value = QuizBase(
        id=quiz_id, title="Old Title", company_id=1
    )
    mock_uow.member.check_is_user_have_permission.return_value = True
    mock_uow.quiz.edit_one.return_value = QuizBase(
        id=quiz_id, title="Updated Quiz", company_id=1
    )

    with pytest.raises(UnAuthorizedException):
        await QuizService.update_quiz(mock_uow, quiz_id, quiz_update, current_user_id=1)


@pytest.mark.asyncio
async def test_update_quiz_not_found(mock_uow):
    quiz_id = 1
    quiz_update = QuizUpdate(title="Updated Quiz", description="Updated Description")
    mock_uow.quiz.find_one.return_value = None

    with pytest.raises(NotFoundException):
        await QuizService.update_quiz(mock_uow, quiz_id, quiz_update, current_user_id=1)


@pytest.mark.asyncio
async def test_get_quiz_by_id_not_found(mock_uow):
    quiz_id = 1
    mock_uow.quiz.find_one.return_value = None

    with pytest.raises(NotFoundException):
        await QuizService.get_quiz_by_id(mock_uow, quiz_id, current_user_id=1)


@pytest.mark.asyncio
async def test_get_quizzes(mock_uow, mock_request):
    company_id = 1
    current_user_id = 1
    mock_uow.member.check_is_user_member_or_higher.return_value = False

    with pytest.raises(TypeError):
        await QuizService.get_quizzes(
            mock_uow, company_id, current_user_id, mock_request
        )
