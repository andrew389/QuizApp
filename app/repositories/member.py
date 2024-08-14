from sqlalchemy import select, func

from app.models import Member
from app.uow.repository import SQLAlchemyRepository


class MemberRepository(SQLAlchemyRepository):
    """
    Repository class for managing `Member` entities in the database.

    Inherits from `SQLAlchemyRepository` and provides methods specific to `Member` entities.
    """

    model = Member

    async def find_owner(self, user_id: int, company_id: int):
        """
        Retrieves a `Member` entity representing the owner of a specific company.

        Args:
            user_id (int): The ID of the user to check.
            company_id (int): The ID of the company to which the user belongs.

        Returns:
            Member: The `Member` entity if the user is an owner of the company; otherwise, `None`.
        """
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
        """
        Retrieves all `Member` entities associated with a specific company with pagination support.

        Args:
            company_id (int): The ID of the company whose members are to be retrieved.
            skip (int): The number of records to skip (used for pagination). Defaults to 0.
            limit (int): The maximum number of records to return (used for pagination). Defaults to 10.

        Returns:
            list[Member]: A list of `Member` entities associated with the specified company.
        """
        stmt = (
            select(self.model)
            .where(self.model.company_id == company_id)
            .offset(skip)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def count_all_by_company(self, company_id: int):
        """
        Counts the number of `Member` entities associated with a specific company.

        Args:
            company_id (int): The ID of the company whose members are to be counted.

        Returns:
            int: The number of `Member` entities associated with the specified company.
        """
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
        """
        Retrieves all `Member` entities associated with a specific company and role with pagination support.

        Args:
            company_id (int): The ID of the company whose members are to be retrieved.
            role (int): The role of the members to be retrieved.
            skip (int): The number of records to skip (used for pagination). Defaults to 0.
            limit (int): The maximum number of records to return (used for pagination). Defaults to 10.

        Returns:
            list[Member]: A list of `Member` entities associated with the specified company and role.
        """
        stmt = (
            select(self.model)
            .where(self.model.company_id == company_id, self.model.role == role)
            .offset(skip)
            .limit(limit)
        )

        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def count_all_by_company_and_role(self, company_id: int, role: int):
        """
        Counts the number of `Member` entities associated with a specific company and role.

        Args:
            company_id (int): The ID of the company whose members are to be counted.
            role (int): The role of the members to be counted.

        Returns:
            int: The number of `Member` entities associated with the specified company and role.
        """
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.company_id == company_id, self.model.role == role)
        )
        res = await self.session.execute(stmt)
        return res.scalar()
