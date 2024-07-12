import secrets
import string
from datetime import timedelta, datetime
from typing import Union

from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from jose.jwt import decode
from jwt import PyJWKClient
from starlette import status

from app.core.config import settings
from app.core.dependencies import token_scheme
from app.models.user import User
from app.repositories.unitofwork import UnitOfWork
from app.schemas.user import UserCreate
from app.services.user import UserService
from app.utils.hasher import Hasher
from fastapi.security import HTTPAuthorizationCredentials

from app.utils.user_create import create_user


class AuthService:
    async def authenticate_user(
        self, uow: UnitOfWork, username: str, password: str
    ) -> Union[User, None]:
        async with uow:
            user = await UserService.get_user_by_username(uow, username)
            if not user or not Hasher.verify_password(password, user.hashed_password):
                return None
            return user

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.auth.secret_key, algorithm=settings.auth.algorithm
        )
        return encoded_jwt

    def verify_token_credentials(self, token: HTTPAuthorizationCredentials):
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def get_payload_from_token(self, token: HTTPAuthorizationCredentials):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            verify_token = VerifyToken(token.credentials)
            if len(str(token.credentials)) > 168:
                payload = verify_token.verify_auth0()
            else:
                payload = verify_token.verify_jwt()
            if "status" in payload and payload["status"] == "error":
                raise credentials_exception
            return payload
        except JWTError:
            raise credentials_exception

    def get_email_from_payload(self, payload: dict):
        email = payload.get("email")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return email

    async def get_user_by_email_or_create(self, uow: UnitOfWork, email: str):
        async with uow:
            user = await UserService.get_user_by_email(uow, email=email)
            if user is None:
                user = await create_user(uow, email)
            return user

    async def get_current_user(
        self,
        token: HTTPAuthorizationCredentials = Depends(token_scheme),
        uow: UnitOfWork = Depends(UnitOfWork),
    ):
        self.verify_token_credentials(token)
        payload = self.get_payload_from_token(token)
        email = self.get_email_from_payload(payload)
        return await self.get_user_by_email_or_create(uow, email)


auth_service = AuthService()


class VerifyToken:
    def __init__(self, token):
        self.token = token
        jwks_url = f"https://{settings.auth.domain}/.well-known/jwks.json"
        self.jwks_client = PyJWKClient(jwks_url)
        self.signing_key = settings.auth.signing_key

    def verify_auth0(self):
        try:
            payload = decode(
                self.token,
                self.signing_key,
                algorithms=[settings.auth.algorithm],
                audience=settings.auth.audience,
                issuer=settings.auth.issuer,
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        return payload

    def verify_jwt(self):
        try:
            payload = jwt.decode(
                self.token,
                settings.auth.secret_key,
                algorithms=[settings.auth.algorithm],
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        return payload
