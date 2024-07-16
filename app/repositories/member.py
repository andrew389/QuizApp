from sqlalchemy import select

from app.models.models import Member
from app.uow.repository import SQLAlchemyRepository


class MemberRepository(SQLAlchemyRepository):
    model = Member

    async def find_owner(self, user_id: int, company_id: int):
        stmt = select(self.model).where(
            self.model.user_id == user_id,
            self.model.company_id == company_id,
            self.model.role == 1,
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

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
