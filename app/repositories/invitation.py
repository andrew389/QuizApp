from sqlalchemy import select, func

from app.models import Invitation
from app.uow.repository import SQLAlchemyRepository


class InvitationRepository(SQLAlchemyRepository):
    """
    Repository class for managing `Invitation` entities in the database.

    Inherits from `SQLAlchemyRepository` and provides methods specific to `Invitation` entities.
    """

    model = Invitation

    async def find_all_by_sender(self, sender_id: int, skip: int = 0, limit: int = 10):
        """
        Retrieves all invitations sent by a specific sender with pagination support.

        Args:
            sender_id (int): The ID of the sender whose invitations are to be retrieved.
            skip (int): The number of records to skip (used for pagination). Defaults to 0.
            limit (int): The maximum number of records to return (used for pagination). Defaults to 10.

        Returns:
            list[Invitation]: A list of `Invitation` entities sent by the specified sender.
        """
        stmt = (
            select(self.model).filter_by(sender_id=sender_id).offset(skip).limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def count_all_by_sender(self, sender_id: int) -> int:
        """
        Counts the number of invitations sent by a specific sender.

        Args:
            sender_id (int): The ID of the sender whose invitations are to be counted.

        Returns:
            int: The number of invitations sent by the specified sender.
        """
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
        """
        Retrieves all invitations received by a specific receiver with pagination support.

        Args:
            receiver_id (int): The ID of the receiver whose invitations are to be retrieved.
            skip (int): The number of records to skip (used for pagination). Defaults to 0.
            limit (int): The maximum number of records to return (used for pagination). Defaults to 10.

        Returns:
            list[Invitation]: A list of `Invitation` entities received by the specified receiver.
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
        Counts the number of invitations received by a specific receiver.

        Args:
            receiver_id (int): The ID of the receiver whose invitations are to be counted.

        Returns:
            int: The number of invitations received by the specified receiver.
        """
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.receiver_id == receiver_id)
        )
        res = await self.session.execute(stmt)
        return res.scalar()
