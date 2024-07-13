from abc import ABC, abstractmethod
from typing import Type

from app.db.pg_db import async_session_maker
from app.repositories.company import CompanyRepository
from app.repositories.user import UserRepository


class IUnitOfWork(ABC):
    user: UserRepository
    company: CompanyRepository

    @abstractmethod
    def __init__(self): ...

    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, *args): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...


class UnitOfWork:
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        self.session = self.session_factory()

        self.user = UserRepository(self.session)
        self.company = CompanyRepository(self.session)

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type:
            await self.rollback()
            raise exc_value
        else:
            await self.commit()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
