from fastapi import APIRouter, Depends, status

from app.core.dependencies import UOWDep, AuthServiceDep, InvitationServiceDep
from app.core.logger import logger
from app.exceptions.base import (
    NotFoundException,
    DeletingException,
)
from app.models.user import User
from app.schemas.invitation import (
    InvitationResponse,
)

router = APIRouter(prefix="/invites", tags=["Invites"])


@router.post(
    "/{invitation_id}/cancel", response_model=dict, status_code=status.HTTP_200_OK
)
async def cancel_invitation_to_user(
    invitation_id: int,
    uow: UOWDep,
    invitation_service: InvitationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Cancel an invitation.
    """
    try:
        canceled_invitation_id = await invitation_service.cancel_invitation(
            uow, invitation_id, current_user.id
        )
        return {"canceled_invitation_id": canceled_invitation_id}
    except Exception as e:
        logger.error(f"Error canceling invitation: {e}")
        raise DeletingException()


@router.post("/{invitation_id}/accept", response_model=InvitationResponse)
async def accept_invitation_for_user(
    invitation_id: int,
    uow: UOWDep,
    invitation_service: InvitationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Accept an invitation.
    """
    try:
        response = await invitation_service.accept_invitation(
            uow, invitation_id, current_user.id
        )
        return response
    except Exception as e:
        logger.error(f"Error accepting invitation: {e}")
        raise Exception()


@router.post("/{invitation_id}/decline", response_model=InvitationResponse)
async def decline_invitation_for_user(
    invitation_id: int,
    uow: UOWDep,
    invitation_service: InvitationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Decline an invitation.
    """
    try:
        response = await invitation_service.decline_invitation(
            uow, invitation_id, current_user.id
        )
        return response
    except Exception as e:
        logger.error(f"Error declining invitation: {e}")
        raise NotFoundException()
