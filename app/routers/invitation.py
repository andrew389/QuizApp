from fastapi import APIRouter, Depends, Query

from app.core.dependencies import UOWDep, AuthServiceDep, InvitationServiceDep
from app.core.logger import logger
from app.exceptions.base import (
    CreatingException,
    FetchingException,
    NotFoundException,
    DeletingException,
)
from app.models.models import User
from app.schemas.invitation import (
    InvitationBase,
    SendInvitation,
    InvitationsListResponse,
    InvitationResponse,
)

router = APIRouter(prefix="/invitation", tags=["Invitation"])


@router.post("/owner/send", response_model=InvitationBase)
async def send_invitation_to_user(
    uow: UOWDep,
    invitation_data: SendInvitation,
    invitation_service: InvitationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        invitation = await invitation_service.send_invitation(
            uow, invitation_data, current_user.id
        )
        return invitation
    except Exception as e:
        logger.error(f"{e}")
        raise CreatingException()


@router.post("/owner/cancel", response_model=dict)
async def cancel_invitation_to_user(
    invitation_id: int,
    uow: UOWDep,
    invitation_service: InvitationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        invitation_id = await invitation_service.cancel_invitation(
            uow, invitation_id, current_user.id
        )
        return {"status_code": 200, "canceled_invitation_id": invitation_id}
    except Exception as e:
        logger.error(f"Error canceling request to join company: {e}")
        raise DeletingException()


@router.post("/user/accept/{invitation_id}", response_model=InvitationResponse)
async def accept_invitation_for_user(
    invitation_id: int,
    uow: UOWDep,
    invitation_service: InvitationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        response = await invitation_service.accept_invitation(
            uow, invitation_id, current_user.id
        )
        return response
    except Exception as e:
        logger.error(f"Error accepting invitation: {e}")
        raise Exception()


@router.post("/user/decline/{invitation_id}", response_model=InvitationResponse)
async def decline_invitation_for_user(
    invitation_id: int,
    uow: UOWDep,
    invitation_service: InvitationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        response = await invitation_service.decline_invitation(
            uow, invitation_id, current_user.id
        )
        return response
    except Exception as e:
        logger.error(f"Error declining invitation: {e}")
        raise NotFoundException()
