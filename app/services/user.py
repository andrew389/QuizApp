from fastapi import Request

from app.core.logger import logger
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserDetail,
    UsersListResponse,
    UserUpdate,
)
from app.uow.unitofwork import IUnitOfWork
from app.utils.hasher import Hasher
from app.utils.user import get_pagination_urls


class UserService:
    """
    Service for managing user accounts within the system.

    This service provides functionalities for adding, retrieving, updating, and deactivating users. It includes
    operations for validating user data, handling permissions, and managing user-related details.

    Methods:
        - add_user: Adds a new user to the system. Ensures that no duplicate email addresses are used.
        - get_users: Retrieves a list of users with pagination support. Returns a list of users and the total count.
        - get_user_by_id: Retrieves a user by their unique ID.
        - get_user_by_username: Retrieves a user by their username.
        - get_user_by_email: Retrieves a user by their email address.
        - validate_user_update: Validates and updates user data, replacing default or empty values with current data.
        - update_user: Updates user details. Ensures that the current user is authorized to perform the update.
        - deactivate_user: Deactivates a user account. Ensures that the current user is authorized to deactivate the user.
    """

    @staticmethod
    async def add_user(uow: IUnitOfWork, user: UserCreate) -> UserBase:
        """
        Add a new user to the system.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            user (UserCreate): The user data to create.

        Returns:
            UserBase: The created user.

        Raises:
            ValueError: If a user with the same email already exists.
        """
        async with uow:
            existing_user = await uow.user.find_one(email=user.email)
            if existing_user:
                logger.error(f"User with email {user.email} already exists.")
                raise ValueError("User with this email already exists.")

            user_dict = user.model_dump()
            user_dict["password"] = Hasher.hash_password(user_dict.pop("password"))

            user_model = await uow.user.add_one(user_dict)

        return UserBase.model_validate(user_model)

    @staticmethod
    async def get_users(
        uow: IUnitOfWork, request: Request, skip: int = 0, limit: int = 10
    ) -> UsersListResponse:
        """
        Retrieve a list of users.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            request (Request): request from endpoint to get base url.
            skip (int, optional): Number of users to skip (default is 0).
            limit (int, optional): Maximum number of users to return (default is 10).

        Returns:
            UsersListResponse: A list of users and the total count.
        """
        async with uow:
            users = await uow.user.find_all(skip=skip, limit=limit)

            total_users = await uow.user.count()

            links = get_pagination_urls(request, skip, limit, total_users)

            user_list = UsersListResponse(
                links=links,
                users=[UserBase.model_validate(user) for user in users],
                total=total_users,
            )
            return UsersListResponse.model_validate(user_list)

    @staticmethod
    async def get_user_by_id(uow: IUnitOfWork, user_id: int) -> UserBase:
        """
        Retrieve a user by their ID.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            user_id (int): The ID of the user to retrieve.

        Returns:
            UserBase: The user data.

        Raises:
            NotFoundException: If the user is not found.
        """
        async with uow:
            user_model = await uow.user.find_one(id=user_id)
            if user_model:
                return UserBase.model_validate(user_model)
            else:
                logger.error(f"User with ID {user_id} not found.")
                raise NotFoundException()

    @staticmethod
    async def get_user_by_username(uow: IUnitOfWork, username: str) -> UserDetail:
        """
        Retrieve a user by their username.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            username (str): The username of the user to retrieve.

        Returns:
            UserDetail: The user details.

        Raises:
            NotFoundException: If the user is not found.
        """
        async with uow:
            user_model = await uow.user.find_one(username=username)
            if user_model:
                return UserDetail.model_validate(user_model)
            else:
                logger.error(f"User with username {username} not found.")
                raise NotFoundException()

    @staticmethod
    async def get_user_by_email(uow: IUnitOfWork, email: str) -> UserDetail:
        """
        Retrieve a user by their email.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            email (str): The email of the user to retrieve.

        Returns:
            UserDetail: The user details.

        Raises:
            NotFoundException: If the user is not found.
        """
        async with uow:
            user_model = await uow.user.find_one(email=email)
            if user_model:
                return UserDetail.model_validate(user_model)
            else:
                logger.error(f"User with email {email} not found.")
                raise NotFoundException()

    @staticmethod
    async def validate_user_update(
        uow: IUnitOfWork, user_id: int, user_update: UserUpdate
    ) -> UserUpdate:
        """
        Validate and update user data, replacing default or empty values with current data.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            user_id (int): The ID of the user to update.
            user_update (UserUpdate): The updated user data.

        Returns:
            UserUpdate: The validated and updated user data.

        Raises:
            NotFoundException: If the user to update is not found.
        """
        current_user = await uow.user.find_one(id=user_id)
        if not current_user:
            logger.error(f"User with ID {user_id} not found.")
            raise NotFoundException()

        user_data = user_update.model_dump()
        fields_to_check = user_data.keys()

        for field_name in fields_to_check:
            field_value = user_data[field_name]
            if field_value in [None, ""]:
                setattr(user_update, field_name, getattr(current_user, field_name))

        return UserUpdate.model_validate(user_update)

    @staticmethod
    async def update_user(
        uow: IUnitOfWork, current_user_id: int, user_id: int, user_update: UserUpdate
    ) -> UserDetail:
        """
        Update user details.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            current_user_id (int): The ID of the current user making the update.
            user_id (int): The ID of the user to update.
            user_update (UserUpdate): The updated user data.

        Returns:
            UserDetail: The updated user details.

        Raises:
            UnAuthorizedException: If the current user is not authorized to update the user.
            NotFoundException: If the user to update is not found.
        """
        async with uow:
            if current_user_id != user_id:
                logger.error(
                    f"User {current_user_id} is not authorized to update user {user_id}."
                )
                raise UnAuthorizedException()

            user_update = await UserService.validate_user_update(
                uow, user_id, user_update
            )
            user_dict = user_update.model_dump()
            user_dict["id"] = user_id

            await uow.user.edit_one(user_id, user_dict)

            updated_user = await uow.user.find_one(id=user_id)

            return UserDetail.model_validate(updated_user)

    @staticmethod
    async def deactivate_user(
        uow: IUnitOfWork, user_id: int, current_user_id: int
    ) -> UserDetail:
        """
        Deactivate a user.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            user_id (int): The ID of the user to deactivate.
            current_user_id (int): The ID of the current user making the request.

        Returns:
            UserDetail: The deactivated user details.

        Raises:
            UnAuthorizedException: If the current user is not authorized to deactivate the user.
            NotFoundException: If the user to deactivate is not found.
        """
        async with uow:
            if current_user_id != user_id:
                logger.error(
                    f"User {current_user_id} is not authorized to deactivate user {user_id}."
                )
                raise UnAuthorizedException()

            user_model = await uow.user.find_one(id=user_id)
            if not user_model:
                logger.error(f"User with ID {user_id} not found.")
                raise NotFoundException()

            user_model.is_active = False

            await uow.user.edit_one(user_id, {"is_active": False})

            return UserDetail.model_validate(user_model)
