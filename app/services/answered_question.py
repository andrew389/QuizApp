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
        Saves the user's answers to a quiz and increments the quiz frequency.
        """
        async with uow:
            for question_id, answer_id in quiz_data.answers.items():
                await AnsweredQuestionService._process_answer(
                    uow, question_id, answer_id, quiz_id, user_id
                )
            await AnsweredQuestionService._increment_quiz_frequency(uow, quiz_id)
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

        if question.quiz_id != quiz_id:
            raise NotFoundException()

        if not question or not answer:
            return

        is_correct = answer.is_correct
        answer_text = answer.text

        quiz = await uow.quiz.find_one(id=quiz_id)

        existing_answered_question = await uow.answered_question.find_one(
            user_id=user_id, question_id=question_id
        )

        if existing_answered_question:
            await AnsweredQuestionService._update_answered_question(
                uow, existing_answered_question.id, answer_id, answer_text, is_correct
            )
        else:
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
    async def _update_answered_question(
        uow: UnitOfWork,
        answered_question_id: int,
        answer_id: int,
        answer_text: str,
        is_correct: bool,
    ):
        """
        Updates an existing answered question record.
        """
        await uow.answered_question.edit_one(
            answered_question_id,
            {
                "answer_id": answer_id,
                "answer_text": answer_text,
                "is_correct": is_correct,
            },
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
        await uow.answered_question.add_one(answered_question_data.dict(exclude={"id"}))

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
    async def calculate_average_score_within_company(
        uow: UnitOfWork, user_id: int, company_id: int
    ) -> float:
        """
        Calculates the average score of a user within a specific company.
        """
        async with uow:
            answered_questions = await uow.answered_question.find_by_user_and_company(
                user_id=user_id, company_id=company_id
            )
            return AnsweredQuestionService._calculate_average_score(answered_questions)

    @staticmethod
    async def calculate_average_score_across_system(
        uow: UnitOfWork, user_id: int
    ) -> float:
        """
        Calculates the average score of a user across the entire system.
        """
        async with uow:
            answered_questions = await uow.answered_question.find_by_user(
                user_id=user_id
            )
            return AnsweredQuestionService._calculate_average_score(answered_questions)

    @staticmethod
    def _calculate_average_score(answered_questions):
        """
        Calculates the average score based on a list of answered questions.
        """
        correct_answers = sum(1 for q in answered_questions if q.is_correct)
        total_answers = len(answered_questions)

        if total_answers == 0:
            return 0.0

        return correct_answers / total_answers
