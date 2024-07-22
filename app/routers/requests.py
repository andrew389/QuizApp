from fastapi import APIRouter, Depends, status

from app.core.dependencies import UOWDep, MemberRequestsDep, AuthServiceDep
from app.core.logger import logger
from app.exceptions.base import (
    DeletingException,
    UpdatingException,
)
from app.models.user import User
from app.schemas.invitation import InvitationResponse

router = APIRouter(prefix="/requests", tags=["Requests"])


@router.post(
    "/{request_id}/cancel", response_model=dict, status_code=status.HTTP_200_OK
)
async def cancel_request_to_join_to_company(
    request_id: int,
    uow: UOWDep,
    member_service: MemberRequestsDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Cancel a join request.
    """
    try:
        request_id = await member_service.cancel_request_to_join(
            uow, request_id, current_user.id
        )
        return {"canceled_request_id": request_id}
    except Exception as e:
        logger.error(f"Error canceling request to join company: {e}")
        raise DeletingException()


@router.post("/{request_id}/accept", response_model=InvitationResponse)
async def accept_request_for_owner(
    request_id: int,
    uow: UOWDep,
    member_service: MemberRequestsDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Accept a request to join a company.
    """
    try:
        invitation = await member_service.accept_request(
            uow, current_user.id, request_id
        )
        return invitation
    except Exception as e:
        logger.error(f"Error accepting request to join company: {e}")
        raise UpdatingException()


@router.post("/{request_id}/decline", response_model=InvitationResponse)
async def decline_request_for_owner(
    request_id: int,
    uow: UOWDep,
    member_service: MemberRequestsDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Decline a request to join a company.
    """
    try:
        response = await member_service.decline_request(
            uow, current_user.id, request_id
        )
        return response
    except Exception as e:
        logger.error(f"Error declining request to join company: {e}")
        raise UpdatingException()
