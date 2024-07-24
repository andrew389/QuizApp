from sqlalchemy import select

from app.models.quiz import Quiz
from app.uow.repository import SQLAlchemyRepository


class QuizRepository(SQLAlchemyRepository):
    model = Quiz

    async def find_all_by_company(
        self, company_id: int, skip: int = 0, limit: int = 10
    ):
        stmt = (
            select(self.model)
            .where(self.model.company_id == company_id)
            .offset(skip)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()
