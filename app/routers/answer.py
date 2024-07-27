from fastapi import APIRouter, Depends, Query, Request
from app.core.dependencies import (
    UOWDep,
    AnswerServiceDep,
    AuthServiceDep,
)
from app.core.logger import logger
from app.exceptions.base import (
    FetchingException,
    CreatingException,
    UpdatingException,
    DeletingException,
)
from app.models.user import User
from app.schemas.answer import (
    AnswerBase,
    AnswerCreate,
    AnswerUpdate,
    AnswersListResponse,
)

router = APIRouter(prefix="/answers", tags=["Answer"])


@router.post("/", response_model=AnswerBase)
async def create_answer(
    answer: AnswerCreate,
    uow: UOWDep,
    answer_service: AnswerServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Creates a new answer.

    Args:
        answer (AnswerCreate): The answer data to create.
        uow (UOWDep): Unit of Work dependency.
        answer_service (AnswerServiceDep): Answer service dependency.
        current_user (User): The currently authenticated user.

    Returns:
        AnswerBase: The created answer.
    """
    try:
        return await answer_service.create_answer(uow, answer, current_user.id)
    except Exception as e:
        logger.error(f"Error creating answer: {e}")
        raise CreatingException()


@router.put("/{answer_id}", response_model=AnswerBase)
async def update_answer(
    answer_id: int,
    answer: AnswerUpdate,
    uow: UOWDep,
    answer_service: AnswerServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Updates an existing answer.

    Args:
        answer_id (int): The ID of the answer to update.
        answer (AnswerUpdate): The updated answer data.
        uow (UOWDep): Unit of Work dependency.
        answer_service (AnswerServiceDep): Answer service dependency.
        current_user (User): The currently authenticated user.

    Returns:
        AnswerBase: The updated answer.
    """
    try:
        return await answer_service.update_answer(
            uow, answer_id, answer, current_user.id
        )
    except Exception as e:
        logger.error(f"Error updating answer: {e}")
        raise UpdatingException()


@router.get("/{answer_id}", response_model=AnswerBase)
async def get_answer_by_id(
    answer_id: int,
    uow: UOWDep,
    answer_service: AnswerServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Retrieves an answer by its ID.

    Args:
        answer_id (int): The ID of the answer to retrieve.
        uow (UOWDep): Unit of Work dependency.
        answer_service (AnswerServiceDep): Answer service dependency.
        current_user (User): The currently authenticated user.

    Returns:
        AnswerBase: The retrieved answer.
    """
    try:
        return await answer_service.get_answer_by_id(uow, answer_id, current_user.id)
    except Exception as e:
        logger.error(f"Error fetching answer: {e}")
        raise FetchingException()


@router.delete("/{answer_id}", response_model=AnswerBase)
async def delete_answer(
    answer_id: int,
    uow: UOWDep,
    answer_service: AnswerServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Deletes an answer by its ID.

    Args:
        answer_id (int): The ID of the answer to delete.
        uow (UOWDep): Unit of Work dependency.
        answer_service (AnswerServiceDep): Answer service dependency.
        current_user (User): The currently authenticated user.

    Returns:
        AnswerBase: The deleted answer.
    """
    try:
        return await answer_service.delete_answer(uow, answer_id, current_user.id)
    except Exception as e:
        logger.error(f"Error deleting answer: {e}")
        raise DeletingException()


@router.get("/", response_model=AnswersListResponse)
async def get_answers(
    company_id: int,
    uow: UOWDep,
    request: Request,
    answer_service: AnswerServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    """
    Retrieves a list of answers for a specified company.

    Args:
        company_id (int): The ID of the company to retrieve answers for.
        uow (UOWDep): Unit of Work dependency.
        answer_service (AnswerServiceDep): Answer service dependency.
        current_user (User): The currently authenticated user.
        skip (int): The number of items to skip (pagination).
        limit (int): The maximum number of items to return.

    Returns:
        AnswersListResponse: The list of answers.
    """
    try:
        answers_list = await answer_service.get_answers(
            uow,
            company_id=company_id,
            current_user_id=current_user.id,
            request=request,
            skip=skip,
            limit=limit,
        )
        return answers_list
    except Exception as e:
        logger.error(f"Error fetching answers: {e}")
        raise FetchingException()
