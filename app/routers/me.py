from fastapi import APIRouter, Depends, status, Query

from app.core.dependencies import UOWDep, AuthServiceDep, InvitationServiceDep
from app.core.logger import logger
from app.exceptions.base import FetchingException
from app.models.user import User
from app.schemas.invitation import InvitationsListResponse
from app.schemas.token import Token
from app.schemas.user import UserResponse, SignInRequest
from app.exceptions.auth import AuthenticationException

router = APIRouter(prefix="/me", tags=["Me"])


@router.post("/login", response_model=Token)
async def login(uow: UOWDep, form_data: SignInRequest, auth_service: AuthServiceDep):
    """
    Authenticate and return a token.
    """
    user = await auth_service.authenticate_user(
        uow, form_data.email, form_data.password
    )
    if not user:
        raise AuthenticationException()
    access_token, expiration = auth_service.create_access_token(
        data={"email": user.email}
    )
    return Token(access_token=access_token, token_type="bearer", expiration=expiration)


@router.get("/", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_info(current_user: User = Depends(AuthServiceDep.get_current_user)):
    """
    Get current user info.
    """
    return UserResponse(user=current_user)


@router.get("/invites", response_model=InvitationsListResponse)
async def get_new_invitations(
    uow: UOWDep,
    invitation_service: InvitationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    """
    Get new invitations.
    """
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
    """
    Get sent invitations.
    """
    try:
        invitations = await invitation_service.get_sent_invitations(
            uow, current_user.id, skip=skip, limit=limit
        )
        return invitations
    except Exception as e:
        logger.error(f"Error fetching sent invitations: {e}")
        raise FetchingException()
