from sqlalchemy import select
from app.models import AnsweredQuestion
from app.uow.repository import SQLAlchemyRepository


class AnsweredQuestionRepository(SQLAlchemyRepository):
    model = AnsweredQuestion

    async def find_by_user_and_company(self, user_id: int, company_id: int):
        query = select(self.model).where(
            (self.model.user_id == user_id) & (self.model.company_id == company_id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def find_by_user(self, user_id: int):
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()
