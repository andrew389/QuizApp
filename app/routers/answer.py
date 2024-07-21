from fastapi import APIRouter, Depends, Query
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

router = APIRouter(prefix="/answer", tags=["Answer"])


@router.post("/answers", response_model=AnswerBase)
async def create_answer(
    answer: AnswerCreate,
    uow: UOWDep,
    answer_service: AnswerServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        return await answer_service.create_answer(uow, answer, current_user.id)
    except Exception as e:
        logger.error(f"Error creating answer: {e}")
        raise CreatingException()


@router.put("/answers/{answer_id}", response_model=AnswerBase)
async def update_answer(
    answer_id: int,
    answer: AnswerUpdate,
    uow: UOWDep,
    answer_service: AnswerServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        return await answer_service.update_answer(
            uow, answer_id, answer, current_user.id
        )
    except Exception as e:
        logger.error(f"Error updating answer: {e}")
        raise UpdatingException()


@router.get("/answers/{answer_id}", response_model=AnswerBase)
async def get_answer_by_id(
    answer_id: int,
    uow: UOWDep,
    answer_service: AnswerServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        return await answer_service.get_answer_by_id(uow, answer_id, current_user.id)
    except Exception as e:
        logger.error(f"Error fetching answer: {e}")
        raise FetchingException()


@router.delete("/answers/{answer_id}", response_model=AnswerBase)
async def delete_answer(
    answer_id: int,
    uow: UOWDep,
    answer_service: AnswerServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        return await answer_service.delete_answer(uow, answer_id, current_user.id)
    except Exception as e:
        logger.error(f"Error deleting answer: {e}")
        raise DeletingException()


@router.get("/answers/", response_model=AnswersListResponse)
async def get_answers(
    company_id: int,
    uow: UOWDep,
    answer_service: AnswerServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    try:
        answers_list = await answer_service.get_answers(
            uow,
            company_id=company_id,
            current_user_id=current_user.id,
            skip=skip,
            limit=limit,
        )
        return answers_list
    except Exception as e:
        logger.error(f"Error fetching answers: {e}")
        raise FetchingException()
