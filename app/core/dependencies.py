from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.repositories.unitofwork import IUnitOfWork, UnitOfWork

UOWDep = Annotated[IUnitOfWork, Depends(UnitOfWork)]
