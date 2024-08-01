from typing import Annotated, Type

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.pg_db import get_async_session
from app.services.analytics import AnalyticsService
from app.services.answer import AnswerService
from app.services.answered_question import AnsweredQuestionService
from app.services.auth import AuthService
from app.services.company import CompanyService
from app.services.data_export import DataExportService
from app.services.data_import import DataImportService
from app.services.invitation import InvitationService
from app.services.member_management import MemberManagement
from app.services.member_queries import MemberQueries
from app.services.member_requests import MemberRequests
from app.services.notification import NotificationService
from app.services.question import QuestionService
from app.services.quiz import QuizService
from app.services.user import UserService
from app.uow.unitofwork import IUnitOfWork, UnitOfWork

UOWDep: Type[IUnitOfWork] = Annotated[IUnitOfWork, Depends(UnitOfWork)]

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]

UserServiceDep = Annotated[UserService, Depends()]

AuthServiceDep = Annotated[AuthService, Depends()]
CurrentUserDep = Annotated[UserService, Depends(AuthService.get_current_user)]

CompanyServiceDep = Annotated[CompanyService, Depends()]

InvitationServiceDep = Annotated[InvitationService, Depends()]
MemberManagementDep = Annotated[MemberManagement, Depends()]
MemberQueriesDep = Annotated[MemberQueries, Depends()]
MemberRequestsDep = Annotated[MemberRequests, Depends()]

QuizServiceDep = Annotated[QuizService, Depends()]
QuestionServiceDep = Annotated[QuestionService, Depends()]
AnswerServiceDep = Annotated[AnswerService, Depends()]
AnsweredQuestionServiceDep = Annotated[AnsweredQuestionService, Depends()]

DataExportServiceDep = Annotated[DataExportService, Depends()]
DataImportServiceDep = Annotated[DataImportService, Depends()]

AnalyticsServiceDep = Annotated[AnalyticsService, Depends()]

NotificationServiceDep = Annotated[NotificationService, Depends()]
