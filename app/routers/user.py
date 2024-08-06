from fastapi import APIRouter, Query, Request
from app.core.dependencies import (
    UOWDep,
    UserServiceDep,
    CurrentUserDep,
)
from app.exceptions.base import (
    DeletingException,
    UpdatingException,
    FetchingException,
    CreatingException,
    NotFoundException,
)
from app.models.user import User
from app.schemas.user import UserResponse, UserCreate, UserUpdate, UsersListResponse
from app.core.logger import logger

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
async def add_user(
    user: UserCreate,
    uow: UOWDep,
    user_service: UserServiceDep,
):
    """
    Creates a new user.

    Args:
        user (UserCreate): Data to create a new user.
        uow (UOWDep): Unit of Work dependency for database operations.
        user_service (UserServiceDep): Service for managing users.

    Returns:
        UserResponse: The created user details.

    Raises:
        CreatingException: If an error occurs during user creation.
    """
    try:
        logger.info(f"Received user data: {user}")
        new_user = await user_service.add_user(uow, user)

        logger.info(f"User created with ID: {new_user.id}")
        return UserResponse(user=new_user)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise CreatingException()


@router.get("/", response_model=UsersListResponse)
async def get_users(
    uow: UOWDep,
    request: Request,
    user_service: UserServiceDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    """
    Retrieves a list of users.

    Args:
        uow (UOWDep): Unit of Work dependency for database operations.
        request (Request): The request object to get base URL.
        user_service (UserServiceDep): Service for managing users.
        skip (int): Number of users to skip (pagination).
        limit (int): Maximum number of users to return.

    Returns:
        UsersListResponse: The list of users.

    Raises:
        FetchingException: If an error occurs during fetching users.
    """
    try:
        users = await user_service.get_users(uow, request, skip=skip, limit=limit)
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise FetchingException()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    uow: UOWDep,
    user_service: UserServiceDep,
):
    """
    Retrieves a user by their ID.

    Args:
        user_id (int): The ID of the user to retrieve.
        uow (UOWDep): Unit of Work dependency for database operations.
        user_service (UserServiceDep): Service for managing users.

    Returns:
        UserResponse: The details of the retrieved user.

    Raises:
        NotFoundException: If the user with the specified ID is not found.
        FetchingException: If an error occurs during fetching the user.
    """
    try:
        user = await user_service.get_user_by_id(uow, user_id)
        if not user:
            logger.warning(f"User with ID {user_id} not found")
            raise NotFoundException()
        logger.info(f"Fetched user with ID: {user_id}")
        return UserResponse(user=user)
    except Exception as e:
        logger.error(f"Error fetching user by ID {user_id}: {e}")
        raise FetchingException()


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    uow: UOWDep,
    user_id: int,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
):
    """
    Updates an existing user.

    Args:
        user_update (UserUpdate): Data to update the user.
        uow (UOWDep): Unit of Work dependency for database operations.
        user_id (int): The ID of the user to update.
        user_service (UserServiceDep): Service for managing users.
        current_user (User): The currently authenticated user.

    Returns:
        UserResponse: The updated user details.

    Raises:
        UpdatingException: If an error occurs during user update.
    """
    try:
        updated_user = await user_service.update_user(
            uow, current_user.id, user_id, user_update
        )
        logger.info(f"Updated user with ID: {current_user.id}")
        return UserResponse(user=updated_user)
    except Exception as e:
        logger.error(f"Error updating user with ID {current_user.id}: {e}")
        raise UpdatingException()


@router.delete("/{user_id}", response_model=dict)
async def deactivate_user(
    user_id: int,
    uow: UOWDep,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
):
    """
    Deactivates a user by their ID.

    Args:
        user_id (int): The ID of the user to deactivate.
        uow (UOWDep): Unit of Work dependency for database operations.
        user_service (UserServiceDep): Service for managing users.
        current_user (User): The currently authenticated user.

    Returns:
        dict: A dictionary with a status code indicating success.

    Raises:
        DeletingException: If an error occurs during user deactivation.
    """
    try:
        deactivated_user_id = await user_service.deactivate_user(
            uow, user_id, current_user.id
        )
        logger.info(f"Deleted user with ID: {deactivated_user_id}")
        return {"status_code": 200}
    except Exception as e:
        logger.error(f"Error deleting user with ID {user_id}: {e}")
        raise DeletingException()
