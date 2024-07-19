import pytest
from unittest.mock import AsyncMock

from app.schemas.answer import (
    AnswerCreate,
    AnswerUpdate,
    AnswerBase,
    AnswersListResponse,
)
from app.services.answer import AnswerService
from app.uow.unitofwork import UnitOfWork
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException


@pytest.mark.asyncio
async def test_create_answer():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.answer = AsyncMock()
    mock_uow.member = AsyncMock()

    answer_data = AnswerCreate(text="Sample text", is_correct=False, company_id=1)
    mock_uow.answer.add_one.return_value = answer_data

    with pytest.raises(UnAuthorizedException):
        await AnswerService.create_answer(mock_uow, answer_data, current_user_id=1)


@pytest.mark.asyncio
async def test_update_answer():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.answer = AsyncMock()
    mock_uow.member = AsyncMock()

    answer_id = 1
    answer_data = AnswerBase(
        text="Updated Answer", is_correct=True, question_id=1, company_id=1
    )
    mock_uow.answer.edit_one.return_value = answer_data
    with pytest.raises(UnAuthorizedException):
        await AnswerService.update_answer(
            mock_uow, answer_id, answer_data, current_user_id=1
        )


@pytest.mark.asyncio
async def test_get_answer_by_id():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.answer = AsyncMock()
    mock_uow.member = AsyncMock()

    answer_id = 1
    mock_answer = AnswerBase(
        id=answer_id, text="Test Answer", is_correct=True, question_id=1, company_id=1
    )
    mock_uow.answer.find_one.return_value = mock_answer

    with pytest.raises(UnAuthorizedException):
        await AnswerService.get_answer_by_id(mock_uow, answer_id, current_user_id=1)


@pytest.mark.asyncio
async def test_get_answers():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.answer = AsyncMock()
    mock_uow.member = AsyncMock()

    company_id = 1
    mock_answers = [
        AnswerBase(
            id=1, text="Test Answer", is_correct=True, question_id=1, company_id=1
        )
    ]
    mock_uow.answer.find_all.return_value = mock_answers

    with pytest.raises(UnAuthorizedException):
        await AnswerService.get_answers(mock_uow, company_id, current_user_id=1)


@pytest.mark.asyncio
async def test_delete_answer():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.answer = AsyncMock()
    mock_uow.member = AsyncMock()

    answer_id = 1
    mock_uow.answer.find_one.return_value = AnswerBase(
        id=answer_id, text="Test Answer", is_correct=True, question_id=1, company_id=1
    )

    with pytest.raises(UnAuthorizedException):
        await AnswerService.delete_answer(mock_uow, answer_id, current_user_id=1)
