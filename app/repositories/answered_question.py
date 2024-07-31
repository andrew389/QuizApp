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
