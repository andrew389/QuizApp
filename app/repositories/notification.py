from sqlalchemy import select, func

from app.models.notification import Notification
from app.uow.repository import SQLAlchemyRepository


class NotificationRepository(SQLAlchemyRepository):
    """
    Repository class for managing `Notification` entities in the database.

    Inherits from `SQLAlchemyRepository` and provides methods specific to `Notification` entities.
    """

    model = Notification

    async def find_all_by_receiver(
        self, receiver_id: int, skip: int = 0, limit: int = 10
    ):
        """
        Retrieves all `Notification` entities for a specific receiver with pagination support.

        Args:
            receiver_id (int): The ID of the user who is the receiver of the notifications.
            skip (int): The number of records to skip (used for pagination). Defaults to 0.
            limit (int): The maximum number of records to return (used for pagination). Defaults to 10.

        Returns:
            list[Notification]: A list of `Notification` entities for the specified receiver.
        """
        stmt = (
            select(self.model)
            .where(self.model.receiver_id == receiver_id)
            .offset(skip)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def count_all_by_receiver(self, receiver_id: int) -> int:
        """
        Counts the number of `Notification` entities for a specific receiver.

        Args:
            receiver_id (int): The ID of the user who is the receiver of the notifications.

        Returns:
            int: The number of `Notification` entities for the specified receiver.
        """
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.receiver_id == receiver_id)
        )
        res = await self.session.execute(stmt)
        return res.scalar()
