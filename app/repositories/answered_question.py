from datetime import datetime

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

    async def find_by_user_and_date_range(
        self, user_id: int, start_date: datetime, end_date: datetime
    ):
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.created_at >= start_date,
            self.model.created_at <= end_date,
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def find_last_attempt(self, user_id: int):
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
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.company_id == company_id,
            self.model.created_at >= start_date,
            self.model.created_at <= end_date,
        )
        result = await self.session.execute(query)
        return result.scalars().all()
