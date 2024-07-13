from datetime import timedelta, datetime

from fastapi import Depends
from jose import jwt, JWTError
from jose.jwt import decode
from jwt import PyJWKClient

from app.core.config import settings
from app.uow.unitofwork import UnitOfWork, IUnitOfWork
from app.services.user import UserService
from app.utils.hasher import Hasher
from app.exceptions.auth import ValidateCredentialsException, NotAuthenticatedException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.utils.user_create import create_user


class AuthService:
    @staticmethod
    async def authenticate_user(uow: IUnitOfWork, username: str, password: str):
        async with uow:
            user = await UserService.get_user_by_username(uow, username)
            if not user or not Hasher.verify_password(password, user.hashed_password):
                return None
            return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
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

    @staticmethod
    def verify_token_credentials(token: HTTPAuthorizationCredentials):
        if not token:
            raise NotAuthenticatedException()

    @staticmethod
    def get_payload_from_token(token: HTTPAuthorizationCredentials):
        try:
            verify_token = VerifyToken(token.credentials)
            if len(str(token.credentials)) > 168:
                payload = verify_token.verify_auth0()
            else:
                payload = verify_token.verify_jwt()
            if "status" in payload and payload["status"] == "error":
                raise ValidateCredentialsException()
            return payload
        except JWTError:
            raise ValidateCredentialsException()

    @staticmethod
    def get_email_from_payload(payload: dict):
        email = payload.get("email")
        if email is None:
            raise ValidateCredentialsException()
        return email

    @staticmethod
    async def get_user_by_email_or_create(uow: IUnitOfWork, email: str):
        async with uow:
            user = await UserService.get_user_by_email(uow, email=email)
            if user is None:
                user = await create_user(uow, email)
            return user

    @staticmethod
    async def get_current_user(
        token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        uow: UnitOfWork = Depends(UnitOfWork),
    ):
        AuthService.verify_token_credentials(token)
        payload = AuthService.get_payload_from_token(token)
        email = AuthService.get_email_from_payload(payload)
        return await AuthService.get_user_by_email_or_create(uow, email)


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
