from fastapi import APIRouter, HTTPException, status, Depends
from app.core.dependencies import UOWDep
from app.schemas.user import UserResponse, UserCreate, UserUpdate, UsersList, UserDetail
from app.services.user import UserService
from app.core.logger import logger

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/create", response_model=UserResponse)
async def add_user(
    user: UserCreate,
    uow: UOWDep,
):
    try:
        new_user = await UserService().add_user(uow, user)
        logger.info(f"User created with ID: {new_user.id}")
        return UserResponse(status_code="200", user=new_user)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error")


@router.get("/all", response_model=UsersList)
async def get_users(
    uow: UOWDep,
):
    try:
        users = await UserService().get_users(uow)
        logger.info("Fetched all users")
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    uow: UOWDep,
):
    try:
        user = await UserService().get_user_by_id(uow, user_id)
        if not user:
            logger.warning(f"User with ID {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        logger.info(f"Fetched user with ID: {user_id}")
        return UserResponse(status_code="200", user=user)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching user by ID {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error")


@router.put("update/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    uow: UOWDep,
):
    try:
        updated_user = await UserService().update_user(uow, user_id, user_update)
        logger.info(f"Updated user with ID: {user_id}")
        return UserResponse(status_code="200", user=updated_user)
    except Exception as e:
        logger.error(f"Error updating user with ID {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error")


@router.delete("/delete/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: int,
    uow: UOWDep,
):
    try:
        deleted_user_id = await UserService().delete_user(uow, user_id)
        logger.info(f"Deleted user with ID: {deleted_user_id}")
        return UserResponse(status_code="200")
    except Exception as e:
        logger.error(f"Error deleting user with ID {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error")
