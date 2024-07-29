from sqlalchemy import select, func

from app.models import Invitation
from app.uow.repository import SQLAlchemyRepository


class InvitationRepository(SQLAlchemyRepository):
    model = Invitation

    async def find_all_by_sender(self, sender_id: int, skip: int = 0, limit: int = 10):
        stmt = (
            select(self.model)
            .where(self.model.sender_id == sender_id)
            .offset(skip)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def count_all_by_sender(self, sender_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.sender_id == sender_id)
        )
        res = await self.session.execute(stmt)
        return res.scalar()

    async def find_all_by_receiver(
        self, receiver_id: int, skip: int = 0, limit: int = 10
    ):
        stmt = (
            select(self.model)
            .where(self.model.receiver_id == receiver_id)
            .offset(skip)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def count_all_by_receiver(self, receiver_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.receiver_id == receiver_id)
        )
        res = await self.session.execute(stmt)
        return res.scalar()
