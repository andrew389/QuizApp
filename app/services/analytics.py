from app.uow.unitofwork import UnitOfWork


class AnalyticsService:
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
            return AnalyticsService._calculate_average_score(answered_questions)

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
            return AnalyticsService._calculate_average_score(answered_questions)

    @staticmethod
    async def calculate_average_score_for_specific_quiz(
        uow: UnitOfWork, user_id: int, quiz_id: int
    ) -> float:
        """
        Calculates the average score of a user for the specific quiz
        """
        async with uow:
            answered_questions = await uow.answered_question.find_one(
                user_id=user_id, quiz_id=quiz_id
            )
            return AnalyticsService._calculate_average_score(answered_questions)

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
