from sqlalchemy import select

from app.models.invitation import Invitation
from app.uow.repository import SQLAlchemyRepository


class InvitationRepository(SQLAlchemyRepository):
    model = Invitation

    async def find_all_by_sender(self, sender_id: int, skip: int = 0, limit: int = 10):
        stmt = (
            select(self.model).filter_by(sender_id=sender_id).offset(skip).limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def find_all_by_receiver(
        self, receiver_id: int, skip: int = 0, limit: int = 10
    ):
        stmt = (
            select(self.model)
            .filter_by(receiver_id=receiver_id)
            .offset(skip)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()
