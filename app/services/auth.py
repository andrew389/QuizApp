from datetime import timedelta, datetime

from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError
from starlette import status

from app.core.config import settings
from app.models.user import User
from app.repositories.unitofwork import UnitOfWork
from app.schemas.token import TokenData
from app.services.user import UserService
from app.utils.hasher import Hasher
from fastapi.security import HTTPBearer


class AuthService:
    async def authenticate_user(
        self, uow: UnitOfWork, username: str, password: str
    ) -> User:
        async with uow:
            user = await UserService.get_user_by_username(uow, username)
            if not user or not Hasher.verify_password(password, user.hashed_password):
                return None
            return user

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.auth.secret_key, algorithm=settings.auth.algorithm
        )
        return encoded_jwt

    async def get_current_user(
        self, token: str = Depends(HTTPBearer()), uow: UnitOfWork = Depends(UnitOfWork)
    ):
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token.credentials,
                settings.auth.secret_key,
                algorithms=[settings.auth.algorithm],
            )
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception

        async with uow:
            user = await UserService.get_user_by_username(
                uow, username=token_data.username
            )
        if user is None:
            raise credentials_exception
        return user


auth_service = AuthService()
