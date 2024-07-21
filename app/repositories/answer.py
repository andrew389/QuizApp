from sqlalchemy import select

from app.models.answer import Answer
from app.uow.repository import SQLAlchemyRepository


class AnswerRepository(SQLAlchemyRepository):
    model = Answer

    async def find_all_by_question_id(self, question_id: int):
        stmt = select(self.model).filter_by(question_id=question_id)
        res = await self.session.execute(stmt)
        return res.scalars().all()
