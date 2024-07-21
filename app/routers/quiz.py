from fastapi import APIRouter, Depends, Query

from app.core.dependencies import (
    UOWDep,
    AnswerServiceDep,
    QuestionServiceDep,
    QuizServiceDep,
    AuthServiceDep,
)
from app.core.logger import logger
from app.exceptions.base import FetchingException
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

router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.post("/answers", response_model=AnswerBase)
async def create_answer(
    answer: AnswerCreate,
    uow: UOWDep,
    answer_service: AnswerServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await answer_service.create_answer(uow, answer, current_user.id)


@router.post("/questions/", response_model=QuestionBase)
async def create_question(
    question: QuestionCreate,
    uow: UOWDep,
    question_service: QuestionServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await question_service.create_question(uow, question, current_user.id)


@router.post("/", response_model=QuizBase)
async def create_quiz(
    quiz: QuizCreate,
    uow: UOWDep,
    quiz_service: QuizServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await quiz_service.create_quiz(uow, quiz, current_user.id)


@router.put("/answers/{answer_id}", response_model=AnswerBase)
async def update_answer(
    answer_id: int,
    answer: AnswerUpdate,
    uow: UOWDep,
    answer_service: AnswerServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await answer_service.update_answer(uow, answer_id, answer, current_user.id)


@router.put("/questions/{question_id}", response_model=QuestionBase)
async def update_question(
    question_id: int,
    question: QuestionUpdate,
    uow: UOWDep,
    question_service: QuestionServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await question_service.update_question(
        uow, question_id, question, current_user.id
    )


@router.put("/{quiz_id}", response_model=QuizBase)
async def update_quiz(
    quiz_id: int,
    quiz: QuizUpdate,
    uow: UOWDep,
    quiz_service: QuizServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await quiz_service.update_quiz(uow, quiz_id, quiz, current_user.id)


@router.get("/answers/{answer_id}", response_model=AnswerBase)
async def get_answer_by_id(
    answer_id: int,
    uow: UOWDep,
    answer_service: AnswerServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await answer_service.get_answer_by_id(uow, answer_id, current_user.id)


@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question_by_id(
    question_id: int,
    uow: UOWDep,
    question_service: QuestionServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await question_service.get_question_by_id(uow, question_id, current_user.id)


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz_by_id(
    quiz_id: int,
    uow: UOWDep,
    quiz_service: QuizServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await quiz_service.get_quiz_by_id(uow, quiz_id, current_user.id)


@router.delete("/answers/{answer_id}", response_model=AnswerBase)
async def delete_answer(
    answer_id: int,
    uow: UOWDep,
    answer_service: AnswerServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await answer_service.delete_answer(uow, answer_id, current_user.id)


@router.delete("/questions/{question_id}", response_model=QuestionBase)
async def delete_question(
    question_id: int,
    uow: UOWDep,
    question_service: QuestionServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await question_service.delete_question(uow, question_id, current_user.id)


@router.delete("/{quiz_id}", response_model=QuizBase)
async def delete_quiz(
    quiz_id: int,
    uow: UOWDep,
    quiz_service: QuizServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await quiz_service.delete_quiz(uow, quiz_id, current_user.id)


@router.get("/quizzes/", response_model=QuizzesListResponse)
async def get_quizzes(
    company_id: int,
    uow: UOWDep,
    quiz_service: QuizServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    try:
        quizzes_list = await quiz_service.get_quizzes(
            uow,
            company_id=company_id,
            current_user_id=current_user.id,
            skip=skip,
            limit=limit,
        )
        return quizzes_list
    except Exception as e:
        logger.error(f"Error fetching quizzes: {e}")
        raise FetchingException()


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
