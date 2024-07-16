from fastapi import APIRouter, Depends, Query

from app.core.dependencies import UOWDep, MemberServiceDep, AuthServiceDep
from app.core.logger import logger
from app.exceptions.base import (
    FetchingException,
    CreatingException,
    DeletingException,
    UpdatingException,
)
from app.models.models import User, Member
from app.schemas.invitation import InvitationBase, InvitationResponse
from app.schemas.member import MembersListResponse, MemberBase

router = APIRouter(prefix="/member", tags=["Member"])


@router.get("/", response_model=MembersListResponse)
async def get_members(
    company_id: int,
    uow: UOWDep,
    member_service: MemberServiceDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    try:
        members = await member_service.get_members(
            uow, company_id=company_id, skip=skip, limit=limit
        )
        return members
    except Exception as e:
        logger.error(f"Error fetching members: {e}")
        raise FetchingException()


@router.post("/request", response_model=InvitationBase)
async def request_to_join_company_for_user(
    company_id: int,
    title: str,
    description: str,
    uow: UOWDep,
    member_service: MemberServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        invitation = await member_service.request_to_join_company(
            uow, current_user.id, company_id, title, description
        )
        return invitation
    except Exception as e:
        logger.error(f"Error requesting to join company: {e}")
        raise CreatingException()


@router.post("/cancel_request", response_model=dict)
async def cancel_request_to_join_for_user(
    invitation_id: int,
    uow: UOWDep,
    member_service: MemberServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        invitation_id = await member_service.cancel_request_to_join(
            uow, invitation_id, current_user.id
        )
        return {"status_code": 200, "canceled_invitation_id": invitation_id}
    except Exception as e:
        logger.error(f"Error canceling request to join company: {e}")
        raise DeletingException()


@router.post("/accept_request", response_model=InvitationResponse)
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


@router.post("/decline_request", response_model=InvitationResponse)
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


@router.post("/remove", response_model=MemberBase)
async def remove_member(
    member_id: int,
    uow: UOWDep,
    member_service: MemberServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        result = await member_service.remove_member(uow, current_user.id, member_id)
        return result
    except Exception as e:
        logger.error(f"Error removing member: {e}")
        raise DeletingException()


@router.post("/leave", response_model=MemberBase)
async def leave_company(
    company_id: int,
    uow: UOWDep,
    member_service: MemberServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        result = await member_service.leave_company(uow, current_user.id, company_id)
        return result
    except Exception as e:
        logger.error(f"Error leaving company: {e}")
        raise DeletingException()
