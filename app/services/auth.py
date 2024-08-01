from datetime import datetime, timedelta

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from jose.jwt import decode
from jwt import PyJWKClient

from app.core.config import settings
from app.exceptions.auth import NotAuthenticatedException, ValidateCredentialsException
from app.schemas.user import UserDetail
from app.services.user import UserService
from app.uow.unitofwork import IUnitOfWork, UnitOfWork
from app.utils.hasher import Hasher
from app.utils.user import create_user


class AuthService:
    """
    Service for handling authentication and token management.

    This service provides functionality for user authentication, token creation, and validation. It includes methods
    to authenticate users, create access tokens, verify token credentials, and retrieve user information from tokens.
    It also supports creating a new user if one does not exist and obtaining the current authenticated user.

    Methods:
        - authenticate_user: Authenticates a user by email and password.
        - create_access_token: Creates an access token with an expiration time.
        - verify_token_credentials: Verifies if the token is provided and valid.
        - get_payload_from_token: Extracts and verifies the payload from the token.
        - get_email_from_payload: Extracts email from the token payload.
        - get_user_by_email_or_create: Gets a user by email or creates a new user if not found.
        - get_current_user: Gets the current user from the provided token.
    """

    @staticmethod
    async def authenticate_user(
        uow: IUnitOfWork, email: str, password: str
    ) -> UserDetail:
        """
        Authenticate user by email and password.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            email (str): The user's email address.
            password (str): The user's password.

        Returns:
            UserDetail: The authenticated user.

        Raises:
            NotAuthenticatedException: If authentication fails.
        """
        async with uow:
            user = await UserService.get_user_by_email(uow, email)

            if user and Hasher.verify_password(password, user.password):
                return user

            raise NotAuthenticatedException()

    @staticmethod
    def create_access_token(data: dict):
        """
        Create an access token with an expiration time.

        Args:
            data (dict): Data to include in the token payload.

        Returns:
            Tuple[str, datetime]: The encoded JWT token and its expiration time.
        """
        expires_delta = timedelta(minutes=settings.auth.access_token_expire_minutes)

        to_encode = data.copy()

        expire = datetime.now() + expires_delta

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode, settings.auth.secret_key, algorithm=settings.auth.algorithm
        )

        return encoded_jwt, expire

    @staticmethod
    def verify_token_credentials(token: HTTPAuthorizationCredentials):
        """
        Verify if the token is provided and valid.

        Args:
            token (HTTPAuthorizationCredentials): The token to verify.

        Raises:
            NotAuthenticatedException: If no token is provided.
        """
        if not token or not token.credentials:
            raise NotAuthenticatedException()

    @staticmethod
    def get_payload_from_token(token: HTTPAuthorizationCredentials):
        """
        Extract and verify the payload from the token.

        Args:
            token (HTTPAuthorizationCredentials): The token to decode.

        Returns:
            dict: The payload extracted from the token.

        Raises:
            ValidateCredentialsException: If token validation fails.
        """
        try:
            verify_token = VerifyToken(token.credentials)

            if len(token.credentials) > 168:
                payload = verify_token.verify_auth0()
            else:
                payload = verify_token.verify_jwt()

            if "status" in payload and payload["status"] == "error":
                raise ValidateCredentialsException()

            return payload

        except JWTError as e:
            raise ValidateCredentialsException() from e

    @staticmethod
    def get_email_from_payload(payload: dict):
        """
        Extract email from the token payload.

        Args:
            payload (dict): The payload from the token.

        Returns:
            str: The email extracted from the payload.

        Raises:
            ValidateCredentialsException: If email is not found in payload.
        """
        email = payload.get("email")

        if email is None:
            raise ValidateCredentialsException()

        return email

    @staticmethod
    async def get_user_by_email_or_create(uow: IUnitOfWork, email: str):
        """
        Get a user by email or create a new user if not found.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            email (str): The user's email address.

        Returns:
            UserDetail: The retrieved or newly created user.
        """
        async with uow:
            user = await UserService.get_user_by_email(uow, email=email)

            if user is None:
                user = create_user(email)
                await UserService.add_user(uow, user)

            return user

    @staticmethod
    async def get_current_user(
        token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        uow: UnitOfWork = Depends(UnitOfWork),
    ) -> UserDetail:
        """
        Get the current user from the provided token.

        Args:
            token (HTTPAuthorizationCredentials): The token provided by the user.
            uow (UnitOfWork): The unit of work for database transactions.

        Returns:
            UserDetail: The current user.

        Raises:
            NotAuthenticatedException: If authentication fails.
        """
        AuthService.verify_token_credentials(token)

        payload = AuthService.get_payload_from_token(token)

        email = AuthService.get_email_from_payload(payload)

        return await AuthService.get_user_by_email_or_create(uow, email)


class VerifyToken:
    def __init__(self, token: str):
        """
        Initialize VerifyToken with the given token.

        Args:
            token (str): The token to verify.
        """
        self.token = token
        jwks_url = f"https://{settings.auth.domain}/.well-known/jwks.json"
        self.jwks_client = PyJWKClient(jwks_url)
        self.signing_key = settings.auth.signing_key

    def verify_auth0(self):
        """
        Verify the token using Auth0.

        Returns:
            dict: The decoded payload or error status.
        """
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
        """
        Verify the token using JWT.

        Returns:
            dict: The decoded payload or error status.
        """
        try:
            payload = jwt.decode(
                self.token,
                settings.auth.secret_key,
                algorithms=[settings.auth.algorithm],
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        return payload
