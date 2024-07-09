from typing import Annotated

from fastapi import Depends

from app.repositories.unitofwork import IUnitOfWork, UnitOfWork
from app.services.user import UserService

UOWDep = Annotated[IUnitOfWork, Depends(UnitOfWork)]
UserServiceDep = Annotated[UserService, Depends()]
