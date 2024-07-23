from sqlalchemy import select

from app.models.notification import Notification
from app.uow.repository import SQLAlchemyRepository


class NotificationRepository(SQLAlchemyRepository):
    model = Notification

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
