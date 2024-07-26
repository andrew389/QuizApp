from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 10):
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, **filter_by):
        raise NotImplementedError

    @abstractmethod
    async def edit_one(self, id: int, data: dict) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, id: int) -> int:
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict) -> Any:
        stmt = insert(self.model).values(**data).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def edit_one(self, id: int, data: dict) -> Any:
        stmt = update(self.model).values(**data).filter_by(id=id).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def find_all(self, skip: int = 0, limit: int = 10):
        stmt = select(self.model).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def find_one(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def delete_one(self, id: int) -> int:
        stmt = delete(self.model).filter_by(id=id).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalars().first()
