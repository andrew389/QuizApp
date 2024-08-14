from sqlalchemy import select

from app.models import Quiz
from app.uow.repository import SQLAlchemyRepository


class QuizRepository(SQLAlchemyRepository):
    """
    Repository class for managing `Quiz` entities in the database.

    Inherits from `SQLAlchemyRepository` and provides methods specific to `Quiz` entities.
    """

    model = Quiz

    async def find_all_by_company(
        self, company_id: int, skip: int = 0, limit: int = 10
    ):
        """
        Retrieves all `Quiz` entities associated with a specific company.

        Args:
            company_id (int): The ID of the company for which quizzes are to be retrieved.
            skip (int, optional): The number of records to skip for pagination. Defaults to 0.
            limit (int, optional): The maximum number of records to return. Defaults to 10.

        Returns:
            list[Quiz]: A list of `Quiz` entities associated with the specified company.
        """
        stmt = (
            select(self.model)
            .where(self.model.company_id == company_id)
            .offset(skip)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()
