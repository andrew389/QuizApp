from fastapi import APIRouter, Depends, Query, Request
from app.core.dependencies import (
    UOWDep,
    QuestionServiceDep,
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
from app.schemas.question import (
    QuestionBase,
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionsListResponse,
)


router = APIRouter(prefix="/questions", tags=["Question"])


@router.post("/", response_model=QuestionBase)
async def create_question(
    question: QuestionCreate,
    uow: UOWDep,
    question_service: QuestionServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Create a new question.
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
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Update an existing question.
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
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Retrieve a question by its ID.
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
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Delete a question by its ID.
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
    current_user: User = Depends(AuthServiceDep.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    """
    Get a list of questions for a company.
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
