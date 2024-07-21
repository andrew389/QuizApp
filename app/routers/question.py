from fastapi import APIRouter, Depends, Query
from app.core.dependencies import (
    UOWDep,
    AnswerServiceDep,
    QuestionServiceDep,
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
from app.schemas.answer import (
    AnswerBase,
    AnswerCreate,
    AnswerUpdate,
    AnswersListResponse,
)
from app.schemas.question import (
    QuestionBase,
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionsListResponse,
)
from app.schemas.quiz import (
    QuizResponse,
    QuizCreate,
    QuizBase,
    QuizzesListResponse,
    QuizUpdate,
)

router = APIRouter(prefix="/question", tags=["Question"])


@router.post("/questions/", response_model=QuestionBase)
async def create_question(
    question: QuestionCreate,
    uow: UOWDep,
    question_service: QuestionServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        return await question_service.create_question(uow, question, current_user.id)
    except Exception as e:
        logger.error(f"Error creating question: {e}")
        raise CreatingException()


@router.put("/questions/{question_id}", response_model=QuestionBase)
async def update_question(
    question_id: int,
    question: QuestionUpdate,
    uow: UOWDep,
    question_service: QuestionServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        return await question_service.update_question(
            uow, question_id, question, current_user.id
        )
    except Exception as e:
        logger.error(f"Error updating question: {e}")
        raise UpdatingException()


@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question_by_id(
    question_id: int,
    uow: UOWDep,
    question_service: QuestionServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        return await question_service.get_question_by_id(
            uow, question_id, current_user.id
        )
    except Exception as e:
        logger.error(f"Error fetching question: {e}")
        raise FetchingException()


@router.delete("/questions/{question_id}", response_model=QuestionBase)
async def delete_question(
    question_id: int,
    uow: UOWDep,
    question_service: QuestionServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        return await question_service.delete_question(uow, question_id, current_user.id)
    except Exception as e:
        logger.error(f"Error deleting question: {e}")
        raise DeletingException()


@router.get("/questions/", response_model=QuestionsListResponse)
async def get_questions(
    company_id: int,
    uow: UOWDep,
    question_service: QuestionServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    try:
        questions_list = await question_service.get_questions(
            uow,
            company_id=company_id,
            current_user_id=current_user.id,
            skip=skip,
            limit=limit,
        )
        return questions_list
    except Exception as e:
        logger.error(f"Error fetching questions: {e}")
        raise FetchingException()
