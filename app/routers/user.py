from fastapi import APIRouter, Depends, Query

from app.core.dependencies import (
    AuthServiceDep,
    InvitationServiceDep,
    UOWDep,
    UserServiceDep,
)
from app.core.logger import logger
from app.exceptions.base import (
    CreatingException,
    DeletingException,
    FetchingException,
    NotFoundException,
    UpdatingException,
)
from app.models.user import User
from app.schemas.invitation import InvitationsListResponse
from app.schemas.user import UserCreate, UserResponse, UsersListResponse, UserUpdate

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
        raise CreatingException()


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
        raise FetchingException()


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
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
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
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        deactivated_user_id = await user_service.deactivate_user(
            uow, user_id, current_user.id
        )
        logger.info(f"Deleted user with ID: {deactivated_user_id}")
        return {"status_code": 200}
    except Exception as e:
        logger.error(f"Error deleting user with ID {user_id}: {e}")
        raise DeletingException()


@router.delete("/{user_id}", response_model=dict)
async def deactivate_user(
    user_id: int,
    uow: UOWDep,
    user_service: UserServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        deactivated_user_id = await user_service.deactivate_user(
            uow, user_id, current_user.id
        )
        logger.info(f"Deleted user with ID: {deactivated_user_id}")
        return {"status_code": 200}
    except Exception as e:
        logger.error(f"Error deleting user with ID {user_id}: {e}")
        raise DeletingException()


@router.get("/invites", response_model=InvitationsListResponse)
async def get_new_invitations(
    uow: UOWDep,
    invitation_service: InvitationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    try:
        invitations = await invitation_service.get_invitations(
            uow, current_user.id, skip=skip, limit=limit
        )
        return invitations
    except Exception as e:
        logger.error(f"Error fetching invitations: {e}")
        raise FetchingException()


@router.get("/requests", response_model=InvitationsListResponse)
async def get_sent_invitations(
    uow: UOWDep,
    invitation_service: InvitationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    try:
        invitations = await invitation_service.get_sent_invitations(
            uow, current_user.id, skip=skip, limit=limit
        )
        return invitations
    except Exception as e:
        logger.error(f"Error fetching invitations for owner: {e}")
        raise FetchingException()
