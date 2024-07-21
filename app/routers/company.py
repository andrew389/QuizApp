from fastapi import APIRouter, Query, Depends

from app.core.dependencies import (
    UOWDep,
    CompanyServiceDep,
    AuthServiceDep,
    MemberServiceDep,
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
from app.schemas.member import MemberBase, MembersListResponse

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


@router.get("/members/", response_model=MembersListResponse)
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


@router.get("/admins", response_model=MembersListResponse)
async def get_admins(
    uow: UOWDep,
    member_service: MemberServiceDep,
    company_id: int,
    skip: int = 0,
    limit: int = 10,
):
    return await member_service.view_admins(uow, company_id, skip, limit)


@router.post("/members/remove", response_model=MemberBase)
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
