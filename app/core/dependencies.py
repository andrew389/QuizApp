from typing import Annotated, Type

from fastapi import Depends

from app.services.company import CompanyService
from app.services.invitation import InvitationService
from app.services.member_management import MemberManagement
from app.services.member_queries import MemberQueries
from app.services.member_requests import MemberRequests
from app.uow.unitofwork import IUnitOfWork, UnitOfWork
from app.services.auth import AuthService
from app.services.user import UserService

UOWDep: Type[IUnitOfWork] = Annotated[IUnitOfWork, Depends(UnitOfWork)]

UserServiceDep = Annotated[UserService, Depends()]

AuthServiceDep = Annotated[AuthService, Depends()]

CompanyServiceDep = Annotated[CompanyService, Depends()]

InvitationServiceDep = Annotated[InvitationService, Depends()]
MemberManagementDep = Annotated[MemberManagement, Depends()]
MemberQueriesDep = Annotated[MemberQueries, Depends()]
MemberRequestsDep = Annotated[MemberRequests, Depends()]
