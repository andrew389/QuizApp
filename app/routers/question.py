from fastapi import APIRouter, Query, Request
from app.core.dependencies import (
    UOWDep,
    QuestionServiceDep,
    CurrentUserDep,
)
from app.core.logger import logger
from app.exceptions.base import (
    FetchingException,
    CreatingException,
    UpdatingException,
    DeletingException,
)

from app.schemas.question import (
    QuestionBase,
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionsListResponse,
)

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.post("/", response_model=QuestionBase)
async def create_question(
    question: QuestionCreate,
    uow: UOWDep,
    question_service: QuestionServiceDep,
    current_user: CurrentUserDep,
):
    """
    Creates a new question.

    Args:
        question (QuestionCreate): The data required to create a new question.
        uow (UOWDep): Unit of Work dependency for database operations.
        question_service (QuestionServiceDep): Service for managing questions.
        current_user (User): The currently authenticated user.

    Returns:
        QuestionBase: The created question details.

    Raises:
        CreatingException: If an error occurs during question creation.
    """
    try:
        return await question_service.create_question(uow, question, current_user.id)
    except Exception as e:
        logger.error(f"Error creating question: {e}")
        raise CreatingException()


@router.put("/{question_id}", response_model=QuestionBase)
async def update_question(
    question_id: int,
    question: QuestionUpdate,
    uow: UOWDep,
    question_service: QuestionServiceDep,
    current_user: CurrentUserDep,
):
    """
    Updates an existing question.

    Args:
        question_id (int): The ID of the question to update.
        question (QuestionUpdate): The data to update the question.
        uow (UOWDep): Unit of Work dependency for database operations.
        question_service (QuestionServiceDep): Service for managing questions.
        current_user (User): The currently authenticated user.

    Returns:
        QuestionBase: The updated question details.

    Raises:
        UpdatingException: If an error occurs during question update.
    """
    try:
        return await question_service.update_question(
            uow, question_id, question, current_user.id
        )
    except Exception as e:
        logger.error(f"Error updating question: {e}")
        raise UpdatingException()


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question_by_id(
    question_id: int,
    uow: UOWDep,
    question_service: QuestionServiceDep,
    current_user: CurrentUserDep,
):
    """
    Retrieves a question by its ID.

    Args:
        question_id (int): The ID of the question to retrieve.
        uow (UOWDep): Unit of Work dependency for database operations.
        question_service (QuestionServiceDep): Service for managing questions.
        current_user (User): The currently authenticated user.

    Returns:
        QuestionResponse: The details of the retrieved question.

    Raises:
        FetchingException: If an error occurs during fetching the question.
    """
    try:
        return await question_service.get_question_by_id(
            uow, question_id, current_user.id
        )
    except Exception as e:
        logger.error(f"Error fetching question: {e}")
        raise FetchingException()


@router.delete("/{question_id}", response_model=QuestionBase)
async def delete_question(
    question_id: int,
    uow: UOWDep,
    question_service: QuestionServiceDep,
    current_user: CurrentUserDep,
):
    """
    Deletes a question by its ID.

    Args:
        question_id (int): The ID of the question to delete.
        uow (UOWDep): Unit of Work dependency for database operations.
        question_service (QuestionServiceDep): Service for managing questions.
        current_user (User): The currently authenticated user.

    Returns:
        QuestionBase: The details of the deleted question.

    Raises:
        DeletingException: If an error occurs during question deletion.
    """
    try:
        return await question_service.delete_question(uow, question_id, current_user.id)
    except Exception as e:
        logger.error(f"Error deleting question: {e}")
        raise DeletingException()


@router.get("/", response_model=QuestionsListResponse)
async def get_questions(
    company_id: int,
    uow: UOWDep,
    request: Request,
    question_service: QuestionServiceDep,
    current_user: CurrentUserDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    """
    Retrieves a list of questions for a company.

    Args:
        company_id (int): The ID of the company for which to retrieve questions.
        uow (UOWDep): Unit of Work dependency for database operations.
        request (Request): The HTTP request object.
        question_service (QuestionServiceDep): Service for managing questions.
        current_user (User): The currently authenticated user.
        skip (int): Number of questions to skip (default is 0).
        limit (int): Maximum number of questions to return (default is 10).

    Returns:
        QuestionsListResponse: The list of questions.

    Raises:
        FetchingException: If an error occurs during fetching the questions.
    """
    try:
        questions_list = await question_service.get_questions(
            uow,
            company_id=company_id,
            current_user_id=current_user.id,
            request=request,
            skip=skip,
            limit=limit,
        )
        return questions_list
    except Exception as e:
        logger.error(f"Error fetching questions: {e}")
        raise FetchingException()
