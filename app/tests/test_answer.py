import pytest
from unittest.mock import AsyncMock, patch
from app.schemas.answer import (
    AnswerCreate,
    AnswerBase,
)
from app.services.answer import AnswerService
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException


@pytest.mark.asyncio
async def test_create_answer_success(mock_uow):
    answer_data = AnswerCreate(text="Sample text", is_correct=False, company_id=1)
    created_answer = AnswerBase(
        id=1, text="Sample text", is_correct=False, question_id=1, company_id=1
    )
    mock_uow.answer.add_one.return_value = created_answer

    with patch(
        "app.services.member_management.MemberManagement"
    ) as MockMemberManagement:
        MockMemberManagement.check_is_user_have_permission = AsyncMock(
            return_value=True
        )
        result = await AnswerService.create_answer(
            mock_uow, answer_data, current_user_id=1
        )

    assert result == created_answer
    mock_uow.answer.add_one.assert_called_once_with(
        answer_data.model_dump(exclude={"id"})
    )


@pytest.mark.asyncio
async def test_update_answer_success(mock_uow):
    answer_id = 1
    answer_data = AnswerCreate(text="Updated Answer", is_correct=True, company_id=1)
    updated_answer = AnswerBase(
        id=answer_id,
        text="Updated Answer",
        is_correct=True,
        question_id=1,
        company_id=1,
    )
    mock_uow.answer.edit_one.return_value = updated_answer

    with patch(
        "app.services.member_management.MemberManagement"
    ) as MockMemberManagement:
        MockMemberManagement.check_is_user_have_permission = AsyncMock(
            return_value=True
        )
        result = await AnswerService.update_answer(
            mock_uow, answer_id, answer_data, current_user_id=1
        )

    assert result == updated_answer
    mock_uow.answer.edit_one.assert_called_once_with(
        answer_id, answer_data.model_dump()
    )


@pytest.mark.asyncio
async def test_get_answer_by_id_success(mock_uow):
    answer_id = 1
    answer_data = AnswerBase(
        id=answer_id, text="Test Answer", is_correct=True, question_id=1, company_id=1
    )
    mock_uow.answer.find_one.return_value = answer_data

    with patch(
        "app.services.member_management.MemberManagement"
    ) as MockMemberManagement:
        MockMemberManagement.check_is_user_have_permission = AsyncMock(
            return_value=True
        )
        result = await AnswerService.get_answer_by_id(
            mock_uow, answer_id, current_user_id=1
        )

    assert result == answer_data
    mock_uow.answer.find_one.assert_called_once_with(id=answer_id)


@pytest.mark.asyncio
async def test_get_answer_by_id_not_found(mock_uow):
    answer_id = 1
    mock_uow.answer.find_one.return_value = None

    with patch(
        "app.services.member_management.MemberManagement"
    ) as MockMemberManagement:
        MockMemberManagement.check_is_user_have_permission = AsyncMock(
            return_value=True
        )
        with pytest.raises(NotFoundException):
            await AnswerService.get_answer_by_id(mock_uow, answer_id, current_user_id=1)


@pytest.mark.asyncio
async def test_get_answers(mock_uow, mock_request):
    company_id = 1
    mock_answers = [
        AnswerBase(
            id=1, text="Test Answer", is_correct=True, question_id=1, company_id=1
        )
    ]
    mock_uow.answer.find_all.return_value = mock_answers

    with pytest.raises(UnAuthorizedException):
        await AnswerService.get_answers(
            mock_uow, company_id, current_user_id=1, request=mock_request
        )


@pytest.mark.asyncio
async def test_delete_answer_success(mock_uow):
    answer_id = 1
    answer_data = AnswerBase(
        id=answer_id, text="Test Answer", is_correct=True, question_id=1, company_id=1
    )
    mock_uow.answer.find_one.return_value = answer_data
    mock_uow.answer.delete_one.return_value = answer_data

    with patch(
        "app.services.member_management.MemberManagement"
    ) as MockMemberManagement:
        MockMemberManagement.check_is_user_have_permission = AsyncMock(
            return_value=True
        )
        result = await AnswerService.delete_answer(
            mock_uow, answer_id, current_user_id=1
        )

    assert result == answer_data
    mock_uow.answer.find_one.assert_called_once_with(id=answer_id)
    mock_uow.answer.delete_one.assert_called_once_with(answer_id)


@pytest.mark.asyncio
async def test_delete_answer_not_found(mock_uow):
    answer_id = 1
    mock_uow.answer.find_one.return_value = None

    with patch(
        "app.services.member_management.MemberManagement"
    ) as MockMemberManagement:
        MockMemberManagement.check_is_user_have_permission = AsyncMock(
            return_value=True
        )
        with pytest.raises(NotFoundException):
            await AnswerService.delete_answer(mock_uow, answer_id, current_user_id=1)
