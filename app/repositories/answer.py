from sqlalchemy import select

from app.models import Answer
from app.uow.repository import SQLAlchemyRepository


class AnswerRepository(SQLAlchemyRepository):
    """
    Repository class for managing `Answer` entities in the database.

    Inherits from `SQLAlchemyRepository` and provides methods specific to `Answer` entities.
    """

    model = Answer

    async def find_all_by_question_id(self, question_id: int):
        """
        Retrieves all answers associated with a specific question.

        Args:
            question_id (int): The ID of the question for which to retrieve answers.

        Returns:
            list[Answer]: A list of `Answer` entities related to the specified question.
        """
        stmt = select(self.model).where(self.model.question_id == question_id)
        res = await self.session.execute(stmt)
        return res.scalars().all()
