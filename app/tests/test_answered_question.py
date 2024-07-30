import pytest
from unittest.mock import AsyncMock
from app.exceptions.base import NotFoundException
from app.schemas.answered_question import SendAnsweredQuiz
from app.services.answered_question import AnsweredQuestionService
from app.uow.unitofwork import UnitOfWork


@pytest.mark.asyncio
async def test_save_answered_quiz_with_invalid_question():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.question = AsyncMock()
    mock_uow.answer = AsyncMock()
    mock_uow.quiz = AsyncMock()
    mock_uow.answered_question = AsyncMock()

    # Mock data
    quiz_data = SendAnsweredQuiz(answers={1: 1})
    user_id = 1
    quiz_id = 1

    # Mock methods
    mock_uow.question.find_one.return_value = AsyncMock(quiz_id=2)  # Invalid quiz_id
    mock_uow.answer.find_one.return_value = AsyncMock(is_correct=True, text="Answer")

    with pytest.raises(NotFoundException):
        await AnsweredQuestionService.save_answered_quiz(
            mock_uow, quiz_data, user_id, quiz_id
        )

    assert mock_uow.answered_question.add_one.call_count == 0
    assert mock_uow.commit.call_count == 0


@pytest.mark.asyncio
async def test_calculate_average_score_within_company():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.answered_question = AsyncMock()

    # Mock data
    user_id = 1
    company_id = 1
    answered_questions = [AsyncMock(is_correct=True), AsyncMock(is_correct=False)]
    mock_uow.answered_question.find_by_user_and_company.return_value = (
        answered_questions
    )

    average_score = (
        await AnsweredQuestionService.calculate_average_score_within_company(
            mock_uow, user_id, company_id
        )
    )

    assert average_score == 0.5


@pytest.mark.asyncio
async def test_calculate_average_score_across_system():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.answered_question = AsyncMock()

    # Mock data
    user_id = 1
    answered_questions = [AsyncMock(is_correct=True), AsyncMock(is_correct=False)]
    mock_uow.answered_question.find_by_user.return_value = answered_questions

    average_score = await AnsweredQuestionService.calculate_average_score_across_system(
        mock_uow, user_id
    )

    assert average_score == 0.5
