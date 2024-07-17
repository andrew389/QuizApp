from fastapi import APIRouter, Depends, status

from app.core.dependencies import UOWDep, MemberServiceDep, AuthServiceDep
from app.core.logger import logger
from app.exceptions.base import (
    CreatingException,
    DeletingException,
    UpdatingException,
)
from app.models.models import User
from app.schemas.invitation import InvitationBase, InvitationResponse
from app.schemas.member import MemberRequest

router = APIRouter(prefix="/member", tags=["Member"])


@router.post("/user/send", response_model=InvitationBase)
async def request_to_join_company_to_owner(
    request: MemberRequest,
    uow: UOWDep,
    member_service: MemberServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        invitation = await member_service.request_to_join_company(
            uow, current_user.id, request
        )
        return invitation
    except Exception as e:
        logger.error(f"Error requesting to join company: {e}")
        raise CreatingException()


@router.post("/user/cancel", response_model=dict, status_code=status.HTTP_200_OK)
async def cancel_request_to_join_to_owner(
    invitation_id: int,
    uow: UOWDep,
    member_service: MemberServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        invitation_id = await member_service.cancel_request_to_join(
            uow, invitation_id, current_user.id
        )
        return {"canceled_invitation_id": invitation_id}
    except Exception as e:
        logger.error(f"Error canceling request to join company: {e}")
        raise DeletingException()


@router.post("/owner/accept/{request_id}", response_model=InvitationResponse)
async def accept_request_for_owner(
    request_id: int,
    uow: UOWDep,
    member_service: MemberServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        invitation = await member_service.accept_request(
            uow, current_user.id, request_id
        )
        return invitation
    except Exception as e:
        logger.error(f"Error accepting request to join company: {e}")
        raise UpdatingException()


@router.post("/owner/decline/{request_id}", response_model=InvitationResponse)
async def decline_request_for_owner(
    request_id: int,
    uow: UOWDep,
    member_service: MemberServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        response = await member_service.decline_request(
            uow, current_user.id, request_id
        )
        return response
    except Exception as e:
        logger.error(f"Error declining request to join company: {e}")
        raise UpdatingException()
