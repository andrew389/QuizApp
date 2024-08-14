from sqlalchemy import select

from app.models import Question
from app.uow.repository import SQLAlchemyRepository


class QuestionRepository(SQLAlchemyRepository):
    """
    Repository class for managing `Question` entities in the database.

    Inherits from `SQLAlchemyRepository` and provides methods specific to `Question` entities.
    """

    model = Question

    async def find_all_by_quiz_id(self, quiz_id: int):
        """
        Retrieves all `Question` entities associated with a specific quiz.

        Args:
            quiz_id (int): The ID of the quiz for which questions are to be retrieved.

        Returns:
            list[Question]: A list of `Question` entities associated with the specified quiz.
        """
        stmt = select(self.model).where(self.model.quiz_id == quiz_id)
        res = await self.session.execute(stmt)
        return res.scalars().all()
