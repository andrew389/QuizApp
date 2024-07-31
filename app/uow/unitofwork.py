from abc import ABC, abstractmethod

from app.db.pg_db import async_session_maker
from app.repositories.answer import AnswerRepository
from app.repositories.answered_question import AnsweredQuestionRepository
from app.repositories.company import CompanyRepository
from app.repositories.invitation import InvitationRepository
from app.repositories.member import MemberRepository
from app.repositories.notification import NotificationRepository
from app.repositories.question import QuestionRepository
from app.repositories.quiz import QuizRepository
from app.repositories.user import UserRepository


class IUnitOfWork(ABC):
    """
    Interface for the Unit of Work pattern.

    Provides a contract for managing transactional operations with multiple repositories.
    """

    user: UserRepository
    company: CompanyRepository
    invitation: InvitationRepository
    member: MemberRepository
    quiz: QuizRepository
    question: QuestionRepository
    answer: AnswerRepository
    answered_question: AnsweredQuestionRepository
    notification: NotificationRepository

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


class UnitOfWork(IUnitOfWork):
    """
    Concrete implementation of the Unit of Work pattern using SQLAlchemy.

    Manages transactional operations across multiple repositories.
    """

    def __init__(self):
        """
        Initializes the Unit of Work with a session factory for creating database sessions.
        """
        self.session_factory = async_session_maker

    async def __aenter__(self):
        """
        Asynchronously enters the context manager, creating a new database session
        and initializing repositories.

        Returns:
            UnitOfWork: The current UnitOfWork instance.
        """
        self.session = self.session_factory()

        self.user = UserRepository(self.session)
        self.company = CompanyRepository(self.session)
        self.invitation = InvitationRepository(self.session)
        self.member = MemberRepository(self.session)
        self.quiz = QuizRepository(self.session)
        self.question = QuestionRepository(self.session)
        self.answer = AnswerRepository(self.session)
        self.answered_question = AnsweredQuestionRepository(self.session)
        self.notification = NotificationRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """
        Asynchronously exits the context manager, committing the transaction if no
        exception was raised or rolling back if an exception occurred.

        Args:
            exc_type (type): The exception type, if an exception was raised.
            exc_value (Exception): The exception instance, if an exception was raised.
            traceback (traceback): The traceback object, if an exception was raised.
        """
        if exc_type:
            await self.rollback()
            await self.session.close()
            raise exc_value
        else:
            await self.commit()
            await self.session.close()

    async def commit(self):
        """
        Commits the current transaction.
        """
        await self.session.commit()

    async def rollback(self):
        """
        Rolls back the current transaction.
        """
        await self.session.rollback()
