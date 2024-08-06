from fastapi import APIRouter, status

from app.core.dependencies import UOWDep, InvitationServiceDep, CurrentUserDep
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
    current_user: CurrentUserDep,
):
    """
    Cancel an invitation by its ID.

    Args:
        invitation_id (int): The ID of the invitation to cancel.
        uow (UOWDep): Unit of Work dependency for database operations.
        invitation_service (InvitationServiceDep): Service for invitation operations.
        current_user (User): The currently authenticated user.

    Returns:
        dict: A dictionary with the ID of the canceled invitation.

    Raises:
        DeletingException: If an error occurs while canceling the invitation.
    """
    try:
        canceled_invitation_id = await invitation_service.cancel_invitation(
            uow, invitation_id, current_user.id
        )
        return {"canceled_invitation_id": canceled_invitation_id}
    except Exception as e:
        logger.error(f"Error canceling request to join company: {e}")
        raise DeletingException()


@router.post("/{invitation_id}/accept", response_model=InvitationResponse)
async def accept_invitation_for_user(
    invitation_id: int,
    uow: UOWDep,
    invitation_service: InvitationServiceDep,
    current_user: CurrentUserDep,
):
    """
    Accept an invitation by its ID.

    Args:
        invitation_id (int): The ID of the invitation to accept.
        uow (UOWDep): Unit of Work dependency for database operations.
        invitation_service (InvitationServiceDep): Service for invitation operations.
        current_user (User): The currently authenticated user.

    Returns:
        InvitationResponse: The details of the accepted invitation.

    Raises:
        Exception: If an error occurs while accepting the invitation.
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
    current_user: CurrentUserDep,
):
    """
    Decline an invitation by its ID.

    Args:
        invitation_id (int): The ID of the invitation to decline.
        uow (UOWDep): Unit of Work dependency for database operations.
        invitation_service (InvitationServiceDep): Service for invitation operations.
        current_user (User): The currently authenticated user.

    Returns:
        InvitationResponse: The details of the declined invitation.

    Raises:
        NotFoundException: If an error occurs while declining the invitation.
    """
    try:
        response = await invitation_service.decline_invitation(
            uow, invitation_id, current_user.id
        )
        return response
    except Exception as e:
        logger.error(f"Error declining invitation: {e}")
        raise NotFoundException()
