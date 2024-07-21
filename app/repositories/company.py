from sqlalchemy import select

from app.models.company import Company
from app.uow.repository import SQLAlchemyRepository


class CompanyRepository(SQLAlchemyRepository):
    model = Company

    async def find_all_visible(self, skip: int = 0, limit: int = 10):
        stmt = (
            select(self.model)
            .filter(self.model.is_visible == True)
            .offset(skip)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def find_all_by_owner(self, owner_id: int, skip: int = 0, limit: int = 10):
        stmt = select(self.model).filter_by(owner_id=owner_id).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()
