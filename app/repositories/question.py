from sqlalchemy import select

from app.models.models import Question
from app.uow.repository import SQLAlchemyRepository


class QuestionRepository(SQLAlchemyRepository):
    model = Question

    async def find_all_by_quiz_id(self, quiz_id: int):
        stmt = select(self.model).filter_by(quiz_id=quiz_id)
        res = await self.session.execute(stmt)
        return res.scalars().all()
