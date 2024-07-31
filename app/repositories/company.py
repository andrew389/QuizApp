from sqlalchemy import select
from app.models import Company
from app.uow.repository import SQLAlchemyRepository


class CompanyRepository(SQLAlchemyRepository):
    """
    Repository class for managing `Company` entities in the database.

    Inherits from `SQLAlchemyRepository` and provides methods specific to `Company` entities.
    """

    model = Company

    async def find_all_visible(self, skip: int = 0, limit: int = 10):
        """
        Retrieves all visible companies with pagination support.

        Args:
            skip (int): The number of records to skip (used for pagination). Defaults to 0.
            limit (int): The maximum number of records to return (used for pagination). Defaults to 10.

        Returns:
            list[Company]: A list of `Company` entities that are marked as visible.
        """
        stmt = (
            select(self.model)
            .where(self.model.is_visible == True)
            .offset(skip)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def find_all_by_owner(self, owner_id: int, skip: int = 0, limit: int = 10):
        """
        Retrieves all companies owned by a specific owner with pagination support.

        Args:
            owner_id (int): The ID of the owner whose companies are to be retrieved.
            skip (int): The number of records to skip (used for pagination). Defaults to 0.
            limit (int): The maximum number of records to return (used for pagination). Defaults to 10.

        Returns:
            list[Company]: A list of `Company` entities that are owned by the specified owner.
        """
        stmt = (
            select(self.model)
            .where(self.model.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()
