from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import delete, insert, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    """
    Abstract base class for repository pattern.

    Defines the interface for CRUD operations that must be implemented by any concrete repository class.
    """

    @abstractmethod
    async def add_one(self, data: dict) -> Any:
        """
        Add a single record to the database.

        Args:
            data (dict): The data for the new record.

        Returns:
            Any: The added record.
        """
        raise NotImplementedError

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 10):
        """
        Retrieve multiple records from the database with pagination.

        Args:
            skip (int): Number of records to skip (default is 0).
            limit (int): Number of records to return (default is 10).

        Returns:
            List[Any]: The list of retrieved records.
        """
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, **filter_by):
        """
        Retrieve a single record from the database based on filters.

        Args:
            **filter_by: Filters to apply to the query.

        Returns:
            Any: The retrieved record or None if not found.
        """
        raise NotImplementedError

    @abstractmethod
    async def edit_one(self, id: int, data: dict) -> Any:
        """
        Update a single record in the database.

        Args:
            id (int): The ID of the record to update.
            data (dict): The data to update.

        Returns:
            Any: The updated record.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, id: int) -> int:
        """
        Delete a single record from the database.

        Args:
            id (int): The ID of the record to delete.

        Returns:
            int: The ID of the deleted record.
        """
        raise NotImplementedError

    @abstractmethod
    async def count(self) -> int:
        """
        Count the total number of records in the database.

        Returns:
            int: The total number of records.
        """
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    """
    Concrete implementation of `AbstractRepository` using SQLAlchemy.

    Provides methods to perform CRUD operations on SQLAlchemy models.
    """

    model = None

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with an SQLAlchemy session.

        Args:
            session (AsyncSession): The SQLAlchemy async session to use.
        """
        self.session = session

    async def add_one(self, data: dict) -> Any:
        """
        Add a single record to the database.

        Args:
            data (dict): The data for the new record.

        Returns:
            Any: The added record.
        """
        stmt = insert(self.model).values(**data).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def edit_one(self, id: int, data: dict) -> Any:
        """
        Update a single record in the database.

        Args:
            id (int): The ID of the record to update.
            data (dict): The data to update.

        Returns:
            Any: The updated record.
        """
        stmt = update(self.model).values(**data).filter_by(id=id).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def find_all(self, skip: int = 0, limit: int = 10):
        """
        Retrieve multiple records from the database with pagination.

        Args:
            skip (int): Number of records to skip (default is 0).
            limit (int): Number of records to return (default is 10).

        Returns:
            List[Any]: The list of retrieved records.
        """
        stmt = select(self.model).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def find_one(self, **filter_by):
        """
        Retrieve a single record from the database based on filters.

        Args:
            **filter_by: Filters to apply to the query.

        Returns:
            Any: The retrieved record or None if not found.
        """
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def delete_one(self, id: int) -> int:
        """
        Delete a single record from the database.

        Args:
            id (int): The ID of the record to delete.

        Returns:
            int: The ID of the deleted record.
        """
        stmt = delete(self.model).filter_by(id=id).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def count(self) -> int:
        """
        Count the total number of records in the database.

        Returns:
            int: The total number of records.
        """
        stmt = select(func.count()).select_from(self.model)
        res = await self.session.execute(stmt)
        return res.scalar()
