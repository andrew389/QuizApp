from sqlalchemy import select, func

from app.models import Member
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

    async def count_all_by_company(self, company_id: int):
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.company_id == company_id)
        )
        res = await self.session.execute(stmt)
        return res.scalar()

    async def find_all_by_company_and_role(
        self, company_id: int, role: int, skip: int = 0, limit: int = 10
    ):
        stmt = (
            select(self.model)
            .where(self.model.company_id == company_id, self.model.role == role)
            .offset(skip)
            .limit(limit)
        )

        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def count_all_by_company_and_role(self, company_id: int, role: int):
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.company_id == company_id, self.model.role == role)
        )
        res = await self.session.execute(stmt)
        return res.scalar()
