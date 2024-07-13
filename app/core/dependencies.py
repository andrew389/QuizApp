from typing import Annotated

from fastapi import Depends

from app.services.company import CompanyService
from app.uow.unitofwork import IUnitOfWork, UnitOfWork
from app.services.auth import AuthService
from app.services.user import UserService

UOWDep = Annotated[IUnitOfWork, Depends(UnitOfWork)]
UserServiceDep = Annotated[UserService, Depends()]
AuthServiceDep = Annotated[AuthService, Depends()]
CompanyServiceDep = Annotated[CompanyService, Depends()]
