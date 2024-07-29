import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import Request

from app.schemas.answer import AnswerBase
from app.schemas.question import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionBase,
)
from app.services.question import QuestionService
from app.uow.unitofwork import UnitOfWork
from app.exceptions.auth import UnAuthorizedException


@pytest.mark.asyncio
async def test_create_question():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.question = AsyncMock()
    mock_uow.member = AsyncMock()
    mock_uow.answer = AsyncMock()

    question_data = QuestionCreate(title="Test Question", company_id=1, answers=[1, 2])
    mock_uow.answer.find_one.return_value = True
    mock_uow.question.add_one.return_value = question_data

    with pytest.raises(UnAuthorizedException):
        await QuestionService.create_question(
            mock_uow, question_data, current_user_id=1
        )


@pytest.mark.asyncio
async def test_update_question():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.question = AsyncMock()
    mock_uow.member = AsyncMock()

    question_id = 1
    question_data = QuestionUpdate(title="Updated Question")
    mock_uow.question.find_one.return_value = QuestionCreate(
        title="Old Question", company_id=1, answers=[1, 2]
    )
    mock_uow.question.edit_one.return_value = question_data

    with pytest.raises(UnAuthorizedException):
        await QuestionService.update_question(
            mock_uow, question_id, question_data, current_user_id=1
        )


@pytest.mark.asyncio
async def test_get_question_by_id():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.question = AsyncMock()
    mock_uow.member = AsyncMock()
    mock_uow.answer = AsyncMock()

    answer1 = AnswerBase(
        id=1, text="Test Answer", is_correct=True, question_id=1, company_id=1
    )
    answer2 = AnswerBase(
        id=2, text="Test Answer", is_correct=True, question_id=1, company_id=1
    )
    answer3 = AnswerBase(
        id=3, text="Test Answer", is_correct=True, question_id=1, company_id=1
    )

    question_id = 1
    mock_question = QuestionResponse(
        id=question_id, title="Test Question", answers=[answer1, answer2, answer3]
    )
    mock_uow.question.find_one.return_value = mock_question

    with pytest.raises(AttributeError):
        await QuestionService.get_question_by_id(
            mock_uow, question_id, current_user_id=1
        )


@pytest.mark.asyncio
async def test_get_questions():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.question = AsyncMock()
    mock_uow.member = AsyncMock()

    request = MagicMock(Request)

    company_id = 1
    mock_questions = [QuestionBase(id=1, title="Test Question", company_id=1)]
    mock_uow.question.find_all.return_value = mock_questions

    with pytest.raises(UnAuthorizedException):
        await QuestionService.get_questions(
            mock_uow, company_id, current_user_id=1, request=request
        )


@pytest.mark.asyncio
async def test_delete_question():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.question = AsyncMock()
    mock_uow.member = AsyncMock()
    mock_uow.answer = AsyncMock()

    question_id = 1
    mock_uow.question.find_one.return_value = QuestionBase(
        id=question_id, title="Test Question", company_id=1
    )

    with pytest.raises(UnAuthorizedException):
        await QuestionService.delete_question(mock_uow, question_id, current_user_id=1)
