from fastapi import APIRouter, Query, Depends, status

from app.core.dependencies import (
    UOWDep,
    CompanyServiceDep,
    AuthServiceDep,
    MemberServiceDep,
    InvitationServiceDep,
)
from app.exceptions.base import (
    UpdatingException,
    DeletingException,
    FetchingException,
    CreatingException,
)

from app.models.user import User
from app.schemas.company import (
    CompanyCreate,
    CompanyDetail,
    CompanyUpdate,
    CompaniesListResponse,
)
from app.core.logger import logger
from app.schemas.invitation import InvitationBase, SendInvitation
from app.schemas.member import MemberBase, MembersListResponse, MemberRequest

router = APIRouter(prefix="/company", tags=["Company"])


@router.post("/", response_model=CompanyDetail)
async def add_company(
    company: CompanyCreate,
    uow: UOWDep,
    company_service: CompanyServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        logger.info(f"Received company data: {company}")
        new_company = await company_service.add_company(
            uow, company, owner_id=current_user.id
        )

        logger.info(f"Company created with ID: {new_company.id}")
        return new_company
    except Exception as e:
        logger.error(f"Error creating company: {e}")
        raise CreatingException()


@router.get("/", response_model=CompaniesListResponse)
async def get_companies(
    uow: UOWDep,
    company_service: CompanyServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    try:
        companies = await company_service.get_companies(
            uow, current_user_id=current_user.id, skip=skip, limit=limit
        )
        return companies
    except Exception as e:
        logger.error(f"Error fetching companies: {e}")
        raise FetchingException()


@router.get("/{company_id}", response_model=CompanyDetail)
async def get_company_by_id(
    company_id: int,
    uow: UOWDep,
    company_service: CompanyServiceDep,
):
    try:
        company = await company_service.get_company_by_id(uow, company_id)
        logger.info(f"Fetched company with ID: {company_id}")
        return company
    except Exception as e:
        logger.error(f"Error fetching company by ID {company_id}: {e}")
        raise FetchingException()


@router.put("/{company_id}", response_model=CompanyDetail)
async def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    uow: UOWDep,
    company_service: CompanyServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        updated_company = await company_service.update_company(
            uow, company_id, current_user.id, company_update
        )
        logger.info(f"Updated company with ID: {company_id}")
        return updated_company
    except Exception as e:
        logger.error(f"Error updating company with ID {company_id}: {e}")
        raise UpdatingException()


@router.delete("/{company_id}", response_model=dict)
async def delete_company(
    company_id: int,
    uow: UOWDep,
    company_service: CompanyServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        deleted_company_id = await company_service.delete_company(
            uow, company_id, current_user.id
        )
        logger.info(f"Deleted company with ID: {deleted_company_id}")
        return {"status_code": 200}
    except Exception as e:
        logger.error(f"Error deleting company with ID {company_id}: {e}")
        raise DeletingException()


@router.post("/{company_id}/admin/{member_id}", response_model=MemberBase)
async def appoint_admin(
    company_id: int,
    member_id: int,
    uow: UOWDep,
    member_service: MemberServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await member_service.appoint_admin(
        uow, current_user.id, company_id, member_id
    )


@router.put("/{company_id}/admin/{member_id}", response_model=MemberBase)
async def remove_admin(
    company_id: int,
    member_id: int,
    uow: UOWDep,
    member_service: MemberServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    return await member_service.remove_admin(
        uow, current_user.id, company_id, member_id
    )


@router.put("/{company_id}/visibility", response_model=CompanyDetail)
async def change_company_visibility(
    company_id: int,
    is_visible: bool,
    uow: UOWDep,
    company_service: CompanyServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        updated_company = await company_service.change_company_visibility(
            uow, company_id, current_user.id, is_visible
        )
        logger.info(f"Changed visibility for company with ID: {company_id}")
        return updated_company
    except Exception as e:
        logger.error(f"Error changing visibility for company with ID {company_id}: {e}")
        raise UpdatingException()


@router.post("/{company_id}/join", response_model=InvitationBase)
async def request_to_join_company_to_owner(
    company_id: int,
    request: MemberRequest,
    uow: UOWDep,
    member_service: MemberServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        invitation = await member_service.request_to_join_company(
            uow, current_user.id, request, company_id
        )
        return invitation
    except Exception as e:
        logger.error(f"Error requesting to join company: {e}")
        raise CreatingException()


@router.post("/{company_id}/invite", response_model=InvitationBase)
async def send_invitation_to_user(
    company_id: int,
    uow: UOWDep,
    invitation_data: SendInvitation,
    invitation_service: InvitationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    try:
        invitation = await invitation_service.send_invitation(
            uow, invitation_data, current_user.id, company_id
        )
        return invitation
    except Exception as e:
        logger.error(f"{e}")
        raise CreatingException()


@router.get("/{company_id}/members", response_model=MembersListResponse)
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


@router.get("/{company_id}/admins", response_model=MembersListResponse)
async def get_admins(
    uow: UOWDep,
    member_service: MemberServiceDep,
    company_id: int,
    skip: int = 0,
    limit: int = 10,
):
    return await member_service.view_admins(uow, company_id, skip, limit)


@router.post("/{member_id}/remove", response_model=MemberBase)
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


@router.post("/{company_id}/leave", response_model=MemberBase)
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
