from datetime import datetime

from sqlalchemy import select
from app.models import AnsweredQuestion
from app.uow.repository import SQLAlchemyRepository


class AnsweredQuestionRepository(SQLAlchemyRepository):
    """
    Repository class for managing `AnsweredQuestion` entities in the database.

    Inherits from `SQLAlchemyRepository` and provides methods specific to `AnsweredQuestion` entities.
    """

    model = AnsweredQuestion

    async def find_by_user_and_company(self, user_id: int, company_id: int):
        """
        Retrieves all answered questions for a specific user within a specific company.

        Args:
            user_id (int): The ID of the user for whom to retrieve answered questions.
            company_id (int): The ID of the company within which to retrieve answered questions.

        Returns:
            list[AnsweredQuestion]: A list of `AnsweredQuestion` entities related to the specified user and company.
        """
        query = select(self.model).where(
            (self.model.user_id == user_id) & (self.model.company_id == company_id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def find_by_user(self, user_id: int):
        """
        Retrieves all answered questions for a specific user.

        Args:
            user_id (int): The ID of the user for whom to retrieve answered questions.

        Returns:
            list[AnsweredQuestion]: A list of `AnsweredQuestion` entities related to the specified user.
        """
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def find_by_user_and_date_range(
        self, user_id: int, start_date: datetime, end_date: datetime
    ):
        """
        Retrieves all answered questions for a specific user within a specified date range.

        Args:
            user_id (int): The ID of the user for whom to retrieve answered questions.
            start_date (datetime): The start date of the date range.
            end_date (datetime): The end date of the date range.

        Returns:
            list[AnsweredQuestion]: A list of `AnsweredQuestion` entities related to the specified user within the date range.
        """
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.created_at >= start_date,
            self.model.created_at <= end_date,
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def find_last_attempt(self, user_id: int):
        """
        Retrieves the most recent answered question for a specific user.

        Args:
            user_id (int): The ID of the user for whom to retrieve the last answered question.

        Returns:
            AnsweredQuestion: The most recent `AnsweredQuestion` entity related to the specified user.
        """
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def find_by_user_company_and_date_range(
        self, user_id: int, company_id: int, start_date: datetime, end_date: datetime
    ):
        """
        Retrieves all answered questions for a specific user within a specific company and date range.

        Args:
            user_id (int): The ID of the user for whom to retrieve answered questions.
            company_id (int): The ID of the company within which to retrieve answered questions.
            start_date (datetime): The start date of the date range.
            end_date (datetime): The end date of the date range.

        Returns:
            list[AnsweredQuestion]: A list of `AnsweredQuestion` entities related to the specified user, company, and date range.
        """
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.company_id == company_id,
            self.model.created_at >= start_date,
            self.model.created_at <= end_date,
        )
        result = await self.session.execute(query)
        return result.scalars().all()
