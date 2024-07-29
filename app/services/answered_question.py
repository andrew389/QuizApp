import json
from datetime import datetime

from app.core.logger import logger
from app.db.redis_db import redis_connection
from app.exceptions.base import NotFoundException
from app.schemas.answered_question import SendAnsweredQuiz, AnsweredQuestionBase
from app.uow.unitofwork import UnitOfWork
from sqlalchemy.exc import NoResultFound


class AnsweredQuestionService:
    @staticmethod
    async def save_answered_quiz(
        uow: UnitOfWork, quiz_data: SendAnsweredQuiz, user_id: int, quiz_id: int
    ):
        """
        Saves the user's answers to a db and redis, also increments the quiz frequency.
        """
        await AnsweredQuestionService._process_quiz_answers(
            uow, quiz_data, user_id, quiz_id
        )

        quiz = await uow.quiz.find_one(id=quiz_id)

        redis_key = f"answered_quiz_{user_id}_{quiz.company_id}_{quiz_id}"
        redis_data_json = await AnsweredQuestionService._prepare_redis_data(
            uow, quiz_data, user_id, quiz_id, quiz.company_id
        )
        await redis_connection.write_with_ttl(
            redis_key, redis_data_json, ttl=48 * 60 * 60
        )

    @staticmethod
    async def _process_quiz_answers(
        uow: UnitOfWork, quiz_data: SendAnsweredQuiz, user_id: int, quiz_id: int
    ):
        """
        Process and save the answers provided for a quiz.
        """
        async with uow:
            for question_id, answer_id in quiz_data.answers.items():
                await AnsweredQuestionService._process_answer(
                    uow, question_id, answer_id, quiz_id, user_id
                )
            await uow.commit()

    @staticmethod
    async def _process_answer(
        uow: UnitOfWork, question_id: int, answer_id: int, quiz_id: int, user_id: int
    ):
        """
        Processes a single answer to a quiz question and saves or updates the answer record.
        """
        question = await uow.question.find_one(id=question_id)
        answer = await uow.answer.find_one(id=answer_id)

        if not question and not answer:
            logger.error(f"Not found: question_id={question_id}, answer_id={answer_id}")
        elif not question:
            logger.error(f"Question not found: question_id={question_id}")
        elif not answer:
            logger.error(f"Answer not found: answer_id={answer_id}")

        if not question or not answer:
            raise NotFoundException()

        if question.quiz_id != quiz_id:
            logger.error(f"Quiz not found: quiz_id={quiz_id}")
            raise NotFoundException()

        is_correct = answer.is_correct
        answer_text = answer.text

        quiz = await uow.quiz.find_one(id=quiz_id)

        await AnsweredQuestionService._add_answered_question(
            uow,
            quiz.company_id,
            quiz_id,
            question_id,
            answer_id,
            answer_text,
            is_correct,
            user_id,
        )

    @staticmethod
    async def _add_answered_question(
        uow: UnitOfWork,
        company_id: int,
        quiz_id: int,
        question_id: int,
        answer_id: int,
        answer_text: str,
        is_correct: bool,
        user_id: int,
    ):
        """
        Adds a new answered question record to the database.
        """
        answered_question_data = AnsweredQuestionBase(
            user_id=user_id,
            company_id=company_id,
            quiz_id=quiz_id,
            question_id=question_id,
            answer_id=answer_id,
            answer_text=answer_text,
            is_correct=is_correct,
        )
        await uow.answered_question.add_one(
            answered_question_data.model_dump(exclude={"id"})
        )

    @staticmethod
    async def _increment_quiz_frequency(uow: UnitOfWork, quiz_id: int):
        """
        Increments the frequency count of a quiz.
        """
        try:
            quiz = await uow.quiz.find_one(id=quiz_id)
            if quiz:
                quiz.frequency += 1
                await uow.quiz.edit_one(quiz_id, {"frequency": quiz.frequency})
        except NoResultFound:
            raise NotFoundException()

    @staticmethod
    async def _prepare_redis_data(
        uow: UnitOfWork,
        quiz_data: SendAnsweredQuiz,
        user_id: int,
        quiz_id: int,
        company_id: int,
    ) -> str:
        """
        Prepares the data for storing in Redis.
        """
        redis_data = {
            "user_id": user_id,
            "quiz_id": quiz_id,
            "company_id": company_id,
            "answers": await AnsweredQuestionService._fetch_answer_details(
                uow, quiz_data
            ),
        }
        return json.dumps(redis_data)

    @staticmethod
    async def _fetch_answer_details(
        uow: UnitOfWork, quiz_data: SendAnsweredQuiz
    ) -> list:
        """
        Fetches detailed information about each answer from the provided quiz data.
        """
        return [
            {
                "question_id": question_id,
                "answer_id": answer_id,
                "answer_text": await AnsweredQuestionService._get_answer_text(
                    uow, answer_id
                ),
                "is_correct": await AnsweredQuestionService._is_correct_answer(
                    uow, answer_id
                ),
                "created_at": datetime.now().isoformat(),
            }
            for question_id, answer_id in quiz_data.answers.items()
        ]

    @staticmethod
    async def _get_answer_text(uow: UnitOfWork, answer_id: int) -> str:
        """
        Get answer text from answer
        """
        answer = await uow.answer.find_one(id=answer_id)
        return answer.text if answer else None

    @staticmethod
    async def _is_correct_answer(uow: UnitOfWork, answer_id: int) -> bool:
        """
        Check is user_answer is correct
        """
        answer = await uow.answer.find_one(id=answer_id)
        return answer.is_correct if answer else False
