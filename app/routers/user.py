from fastapi import APIRouter, Query
from app.core.dependencies import UOWDep, UserServiceDep
from app.exceptions.user import (
    DeletingUserException,
    UpdatingUserException,
    FetchingUserException,
    CreatingUserException,
    NotFoundUserException,
)
from app.schemas.user import UserResponse, UserCreate, UserUpdate, UsersListResponse
from app.core.logger import logger

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/", response_model=UserResponse)
async def add_user(
    user: UserCreate,
    uow: UOWDep,
    user_service: UserServiceDep,
):
    try:
        logger.info(f"Received user data: {user}")
        new_user = await user_service.add_user(uow, user)

        logger.info(f"User created with ID: {new_user.id}")
        return UserResponse(user=new_user)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise CreatingUserException()


@router.get("/", response_model=UsersListResponse)
async def get_users(
    uow: UOWDep,
    user_service: UserServiceDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    try:
        users = await user_service.get_users(uow, skip=skip, limit=limit)
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise FetchingUserException()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    uow: UOWDep,
    user_service: UserServiceDep,
):
    try:
        user = await user_service.get_user_by_id(uow, user_id)
        if not user:
            logger.warning(f"User with ID {user_id} not found")
            raise NotFoundUserException()
        logger.info(f"Fetched user with ID: {user_id}")
        return UserResponse(user=user)
    except Exception as e:
        logger.error(f"Error fetching user by ID {user_id}: {e}")
        raise FetchingUserException()


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    uow: UOWDep,
    user_service: UserServiceDep,
):
    try:
        updated_user = await user_service.update_user(uow, user_id, user_update)
        logger.info(f"Updated user with ID: {user_id}")
        return UserResponse(user=updated_user)
    except Exception as e:
        logger.error(f"Error updating user with ID {user_id}: {e}")
        raise UpdatingUserException()


@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    uow: UOWDep,
    user_service: UserServiceDep,
):
    try:
        deleted_user_id = await user_service.delete_user(uow, user_id)
        logger.info(f"Deleted user with ID: {deleted_user_id}")
        return {"status_code": 200}
    except Exception as e:
        logger.error(f"Error deleting user with ID {user_id}: {e}")
        raise DeletingUserException()
