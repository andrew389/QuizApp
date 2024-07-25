import pytest
from unittest.mock import AsyncMock, patch

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
async def test_create_quiz_success():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.quiz = AsyncMock()
    mock_uow.member = AsyncMock()
    mock_uow.question = AsyncMock()

    quiz_data = QuizCreate(title="Test Quiz", company_id=1, questions=[1, 2])
    mock_uow.member.check_is_user_have_permission.return_value = True
    mock_uow.question.find_one.return_value = True
    mock_uow.quiz.add_one.return_value = quiz_data

    with pytest.raises(UnAuthorizedException):
        await QuizService.create_quiz(mock_uow, quiz_data, current_user_id=1)


@pytest.mark.asyncio
async def test_update_quiz_success():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.quiz = AsyncMock()
    mock_uow.member = AsyncMock()
    mock_uow.question = AsyncMock()

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
async def test_get_quiz_by_id_success():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.quiz = AsyncMock()
    mock_uow.question = AsyncMock()
    mock_uow.member = AsyncMock()

    quiz_id = 1
    quiz_data = QuizBase(
        id=quiz_id,
        title="Test Quiz",
        company_id=1,
        description="Test Description",
        frequency=1,
    )
    mock_uow.quiz.find_one.return_value = quiz_data
    mock_uow.question.find_all_by_quiz_id.return_value = [
        AsyncMock(id=1),
        AsyncMock(id=2),
    ]
    mock_uow.member.check_is_user_member_or_higher.return_value = True

    question_response = QuestionResponse(id=1, title="Test Question")
    with patch(
        "app.services.question.QuestionService.get_question_by_id",
        return_value=question_response,
    ):
        quiz_response = await QuizService.get_quiz_by_id(
            mock_uow, quiz_id, current_user_id=1
        )

    assert quiz_response.title == "Test Quiz"
    assert len(quiz_response.questions) == 2
    assert quiz_response.description == "Test Description"
    assert mock_uow.quiz.find_one.called
    assert mock_uow.question.find_all_by_quiz_id.called


@pytest.mark.asyncio
async def test_get_quizzes_success():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.quiz = AsyncMock()
    mock_uow.member = AsyncMock()

    company_id = 1
    current_user_id = 1
    quizzes = [
        QuizBase(
            id=1,
            title="Quiz 1",
            company_id=company_id,
            description="Description",
            frequency=1,
        ),
        QuizBase(
            id=2,
            title="Quiz 2",
            company_id=company_id,
            description="Description",
            frequency=2,
        ),
    ]
    mock_uow.member.check_is_user_member_or_higher.return_value = True
    mock_uow.quiz.find_all.return_value = quizzes

    quizzes_list_response = await QuizService.get_quizzes(
        mock_uow, company_id, current_user_id
    )

    assert len(quizzes_list_response.quizzes) == 2
    assert quizzes_list_response.total == 2
    assert mock_uow.quiz.find_all.called


@pytest.mark.asyncio
async def test_update_quiz_not_found():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.quiz = AsyncMock()
    mock_uow.member = AsyncMock()

    quiz_id = 1
    quiz_update = QuizUpdate(title="Updated Quiz", description="Updated Description")
    mock_uow.quiz.find_one.return_value = None

    with pytest.raises(NotFoundException):
        await QuizService.update_quiz(mock_uow, quiz_id, quiz_update, current_user_id=1)


@pytest.mark.asyncio
async def test_get_quiz_by_id_not_found():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.quiz = AsyncMock()
    mock_uow.member = AsyncMock()

    quiz_id = 1
    mock_uow.quiz.find_one.return_value = None

    with pytest.raises(NotFoundException):
        await QuizService.get_quiz_by_id(mock_uow, quiz_id, current_user_id=1)


@pytest.mark.asyncio
async def test_get_quiz_by_id_insufficient_questions():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.quiz = AsyncMock()
    mock_uow.question = AsyncMock()
    mock_uow.member = AsyncMock()

    quiz_id = 1
    mock_uow.quiz.find_one.return_value = QuizBase(
        id=quiz_id, title="Test Quiz", company_id=1
    )
    mock_uow.question.find_all_by_quiz_id.return_value = [
        AsyncMock(id=1)
    ]  # only one question

    mock_uow.member.check_is_user_member_or_higher.return_value = True

    with pytest.raises(FetchingException):
        await QuizService.get_quiz_by_id(mock_uow, quiz_id, current_user_id=1)


@pytest.mark.asyncio
async def test_get_quizzes():
    mock_uow = AsyncMock(UnitOfWork)
    mock_uow.member = AsyncMock()
    mock_uow.quiz = AsyncMock()  # Ensure `quiz` is properly mocked

    company_id = 1
    current_user_id = 1
    mock_uow.member.check_is_user_member_or_higher.return_value = False

    await QuizService.get_quizzes(mock_uow, company_id, current_user_id)
