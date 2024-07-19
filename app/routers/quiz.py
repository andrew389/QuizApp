from fastapi import APIRouter, Depends

from app.core.dependencies import (
    UOWDep,
    AnswerServiceDep,
    QuestionServiceDep,
    QuizServiceDep,
    AuthServiceDep,
)
from app.models.models import User
from app.schemas.answer import AnswerBase, AnswerCreate, AnswerUpdate
from app.schemas.question import (
    QuestionBase,
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
)
from app.schemas.quiz import QuizResponse, QuizCreate, QuizBase

router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.post("/answers", response_model=AnswerBase)
async def create_answer(
    answer: AnswerCreate,
    uow: UOWDep,
    answer_service: AnswerServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await answer_service.create_answer(uow, answer, current_user.id)


@router.put("/answers/{answer_id}", response_model=AnswerBase)
async def update_answer(
    answer_id: int,
    answer: AnswerUpdate,
    uow: UOWDep,
    answer_service: AnswerServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await answer_service.update_answer(uow, answer_id, answer, current_user.id)


@router.get("/answers/{answer_id}", response_model=AnswerBase)
async def get_answer_by_id(
    answer_id: int,
    uow: UOWDep,
    answer_service: AnswerServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await answer_service.get_answer_by_id(uow, answer_id, current_user.id)


@router.delete("/answers/{answer_id}", response_model=AnswerBase)
async def delete_answer(
    answer_id: int,
    uow: UOWDep,
    answer_service: AnswerServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await answer_service.delete_answer(uow, answer_id, current_user.id)


@router.post("/questions/", response_model=QuestionBase)
async def create_question_endpoint(
    question: QuestionCreate,
    uow: UOWDep,
    question_service: QuestionServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await question_service.create_question(uow, question, current_user.id)


@router.put("/questions/{question_id}", response_model=QuestionBase)
async def update_question_endpoint(
    question_id: int,
    question: QuestionUpdate,
    uow: UOWDep,
    question_service: QuestionServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await question_service.update_question(
        uow, question_id, question, current_user.id
    )


@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question_by_id_endpoint(
    question_id: int,
    uow: UOWDep,
    question_service: QuestionServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await question_service.get_question_by_id(uow, question_id, current_user.id)


@router.delete("/questions/{question_id}", response_model=QuestionBase)
async def delete_question_endpoint(
    question_id: int,
    uow: UOWDep,
    question_service: QuestionServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await question_service.delete_question(uow, question_id, current_user.id)


@router.post("/", response_model=QuizBase)
async def create_quiz_endpoint(
    quiz: QuizCreate,
    uow: UOWDep,
    quiz_service: QuizServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await quiz_service.create_quiz(uow, quiz, current_user.id)


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz_by_id_endpoint(
    quiz_id: int,
    uow: UOWDep,
    quiz_service: QuizServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await quiz_service.get_quiz_by_id(uow, quiz_id, current_user.id)
