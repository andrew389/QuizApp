from fastapi import APIRouter, Depends
from app.core.dependencies import (
    UOWDep,
    QuizServiceDep,
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
from app.schemas.quiz import (
    QuizResponse,
    QuizCreate,
    QuizBase,
    QuizUpdate,
)

router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.post("/", response_model=QuizBase)
async def create_quiz(
    quiz: QuizCreate,
    uow: UOWDep,
    quiz_service: QuizServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        return await quiz_service.create_quiz(uow, quiz, current_user.id)
    except Exception as e:
        logger.error(f"Error creating quiz: {e}")
        raise CreatingException()


@router.put("/{quiz_id}", response_model=QuizBase)
async def update_quiz(
    quiz_id: int,
    quiz: QuizUpdate,
    uow: UOWDep,
    quiz_service: QuizServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        return await quiz_service.update_quiz(uow, quiz_id, quiz, current_user.id)
    except Exception as e:
        logger.error(f"Error updating quiz: {e}")
        raise UpdatingException()


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz_by_id(
    quiz_id: int,
    uow: UOWDep,
    quiz_service: QuizServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        return await quiz_service.get_quiz_by_id(uow, quiz_id, current_user.id)
    except Exception as e:
        logger.error(f"Error fetching quiz: {e}")
        raise FetchingException()


@router.delete("/{quiz_id}", response_model=QuizBase)
async def delete_quiz(
    quiz_id: int,
    uow: UOWDep,
    quiz_service: QuizServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        return await quiz_service.delete_quiz(uow, quiz_id, current_user.id)
    except Exception as e:
        logger.error(f"Error deleting quiz: {e}")
        raise DeletingException()
