from collections import defaultdict
from datetime import datetime
from typing import Dict

from app.exceptions.auth import UnAuthorizedException
from app.services.member_management import MemberManagement
from app.uow.unitofwork import UnitOfWork
from app.utils.role import Role


class AnalyticsService:
    """
    Service for performing analytics-related operations involving user quiz performance.

    This service provides methods to calculate and retrieve various analytics metrics related to quizzes
    and user performance within a company or across the entire system. It includes functionality to compute
    average scores, list users' last quiz attempts, and retrieve detailed scores within specified time ranges.

    Methods:
        - calculate_average_score_within_company: Computes the average quiz score for a specific user within a company.
        - calculate_average_score_across_system: Computes the average quiz score for a user across the entire system.
        - calculate_average_scores_by_quiz: Calculates average scores for each quiz taken by a user within a given time range.
        - get_last_completion_timestamps: Retrieves the last completion timestamp for each quiz taken by a user.
        - calculate_company_members_average_scores: Computes average scores for all members of a company within a specified time range.
        - list_users_last_quiz_attempts: Lists all users in a company with the timestamp of their last quiz attempt.
        - calculate_detailed_average_scores: Provides detailed average scores for each quiz taken by a user within a specified time range and company.
    """

    @staticmethod
    async def calculate_average_score_within_company(
        uow: UnitOfWork, user_id: int, company_id: int
    ) -> float:
        """
        Calculates the average score of a user within a specific company.

        Args:
            uow (UnitOfWork): An instance of UnitOfWork for database operations.
            user_id (int): The ID of the user whose average score is to be calculated.
            company_id (int): The ID of the company within which the average score is calculated.

        Returns:
            float: The average score of the user within the specified company.

        Raises:
            Exception: If there is an error during the database operations.
        """
        async with uow:
            # Fetch answered questions for the specified user and company
            answered_questions = await uow.answered_question.find_by_user_and_company(
                user_id=user_id, company_id=company_id
            )
            # Calculate and return the average score
            return AnalyticsService._calculate_average_score(answered_questions)

    @staticmethod
    async def calculate_average_score_across_system(
        uow: UnitOfWork, user_id: int
    ) -> float:
        """
        Calculates the average score of a user across the entire system.

        Args:
            uow (UnitOfWork): An instance of UnitOfWork for database operations.
            user_id (int): The ID of the user whose average score is to be calculated.

        Returns:
            float: The average score of the user across the entire system.

        Raises:
            Exception: If there is an error during the database operations.
        """
        async with uow:
            # Fetch answered questions for the specified user across the entire system
            answered_questions = await uow.answered_question.find_by_user(
                user_id=user_id
            )
            # Calculate and return the average score
            return AnalyticsService._calculate_average_score(answered_questions)

    @staticmethod
    async def calculate_average_scores_by_quiz(
        uow: UnitOfWork, user_id: int, start_date: datetime, end_date: datetime
    ) -> Dict[int, float]:
        """
        Calculates average scores for each quiz taken by a user within a specified time range.
        """
        async with uow:
            answered_questions = (
                await uow.answered_question.find_by_user_and_date_range(
                    user_id=user_id, start_date=start_date, end_date=end_date
                )
            )

            quiz_scores = {}
            for question in answered_questions:
                quiz_id = question.quiz_id
                if quiz_id not in quiz_scores:
                    quiz_scores[quiz_id] = []
                quiz_scores[quiz_id].append(question)

            average_scores = {
                quiz_id: AnalyticsService._calculate_average_score(questions)
                for quiz_id, questions in quiz_scores.items()
            }

            return average_scores

    @staticmethod
    async def get_last_completion_timestamps(
        uow: UnitOfWork, user_id: int
    ) -> Dict[int, datetime]:
        """
        Retrieves the last completion timestamp for each quiz taken by a user.

        Args:
            uow (UnitOfWork): An instance of UnitOfWork for database operations.
            user_id (int): The ID of the user whose last completion timestamps are to be retrieved.

        Returns:
            Dict[int, datetime]: A dictionary where keys are quiz IDs and values are last completion timestamps.
        """
        async with uow:
            answered_questions = await uow.answered_question.find_by_user(
                user_id=user_id
            )

            last_completion = {}
            for question in answered_questions:
                quiz_id = question.quiz_id
                if (
                    quiz_id not in last_completion
                    or question.created_at > last_completion[quiz_id]
                ):
                    last_completion[quiz_id] = question.created_at

            return last_completion

    @staticmethod
    async def calculate_company_members_average_scores(
        uow: UnitOfWork,
        current_user_id: int,
        company_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[int, float]:
        """
        Calculates average scores for all members of a company within a specified time range.
        Returns a dictionary with member IDs as keys and their average scores as values.

        Args:
            uow (UnitOfWork): An instance of UnitOfWork for database operations.
            current_user_id (int): The ID of the current user requesting the data.
            company_id (int): The ID of the company.
            start_date (datetime): The start date of the time range.
            end_date (datetime): The end date of the time range.

        Returns:
            Dict[int, float]: A dictionary where keys are member IDs and values are average scores.
        """
        async with uow:
            member = await uow.member.find_one(user_id=current_user_id)
            has_permission = await MemberManagement.check_is_user_have_permission(
                uow, current_user_id, member.company_id
            )

            if not has_permission:
                raise UnAuthorizedException()

            members = await uow.member.find_all_by_company_and_role(
                company_id=company_id, role=Role.MEMBER.value
            )

            member_scores = {}
            for member in members:
                user_id = member.user_id
                answered_questions = (
                    await uow.answered_question.find_by_user_and_date_range(
                        user_id=user_id, start_date=start_date, end_date=end_date
                    )
                )
                average_score = AnalyticsService._calculate_average_score(
                    answered_questions
                )
                member_scores[user_id] = average_score

            return member_scores

    @staticmethod
    async def list_users_last_quiz_attempts(
        uow: UnitOfWork, current_user_id: int, company_id: int
    ) -> Dict[int, datetime]:
        """
        Lists all users in a company with the timestamp of their last quiz attempt.
        Returns a dictionary with user IDs as keys and timestamps as values.

        Args:
            uow (UnitOfWork): An instance of UnitOfWork for database operations.
            current_user_id (int): The ID of the current user requesting the data.
            company_id (int): The ID of the company.

        Returns:
            Dict[int, datetime]: A dictionary where keys are user IDs and values are last quiz attempt timestamps.
        """
        async with uow:
            member = await uow.member.find_one(user_id=current_user_id)
            has_permission = await MemberManagement.check_is_user_have_permission(
                uow, current_user_id, member.company_id
            )

            if not has_permission:
                raise UnAuthorizedException()

            members = await uow.member.find_all_by_company_and_role(
                company_id=company_id, role=Role.MEMBER.value
            )

            last_attempts = {}
            for member in members:
                user_id = member.user_id
                last_attempt = await uow.answered_question.find_last_attempt(
                    user_id=user_id
                )
                if last_attempt:
                    last_attempts[user_id] = last_attempt.created_at

            return last_attempts

    @staticmethod
    async def calculate_detailed_average_scores(
        uow: UnitOfWork,
        current_user_id: int,
        user_id: int,
        company_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[int, float]:
        """
        Provides detailed average scores for each quiz taken by a user within a specified time range and company.
        Returns a dictionary with quiz IDs as keys and average scores as values.

        Args:
            uow (UnitOfWork): An instance of UnitOfWork for database operations.
            current_user_id (int): The ID of the current user requesting the data.
            user_id (int): The ID of the user whose scores are to be calculated.
            company_id (int): The ID of the company.
            start_date (datetime): The start date of the time range.
            end_date (datetime): The end date of the time range.

        Returns:
            Dict[int, float]: A dictionary where keys are quiz IDs and values are average scores.
        """
        async with uow:
            member = await uow.member.find_one(user_id=current_user_id)
            has_permission = await MemberManagement.check_is_user_have_permission(
                uow, current_user_id, member.company_id
            )

            if not has_permission:
                raise UnAuthorizedException()

            answered_questions = (
                await uow.answered_question.find_by_user_company_and_date_range(
                    user_id=user_id,
                    company_id=company_id,
                    start_date=start_date,
                    end_date=end_date,
                )
            )

            quiz_scores = defaultdict(list)
            for question in answered_questions:
                quiz_scores[question.quiz_id].append(question)

            detailed_average_scores = {
                quiz_id: AnalyticsService._calculate_average_score(questions)
                for quiz_id, questions in quiz_scores.items()
            }

            return detailed_average_scores

    @staticmethod
    def _calculate_average_score(answered_questions):
        """
        Calculates the average score based on a list of answered questions.

        Args:
            answered_questions (List[AnsweredQuestion]): A list of answered questions.

        Returns:
            float: The average score, rounded to two decimal places.
        """
        correct_answers = sum(1 for q in answered_questions if q.is_correct)
        total_answers = len(answered_questions)

        if total_answers == 0:
            return 0.0

        return round(correct_answers / total_answers, 2)
