from fastapi import APIRouter, Query, Depends
from typing import List

from app.core.dependencies import UOWDep, CompanyServiceDep, AuthServiceDep
from app.exceptions.base import (
    UpdatingException,
    DeletingException,
    FetchingException,
    CreatingException,
)
from app.exceptions.company import NotFoundCompanyException

from app.exceptions.auth import UnAuthorizedException
from app.models.models import User
from app.schemas.company import (
    CompanyCreate,
    CompanyDetail,
    CompanyUpdate,
    CompaniesListResponse,
)
from app.core.logger import logger

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
        if not company:
            logger.warning(f"Company with ID {company_id} not found")
            raise NotFoundCompanyException()
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
        company = await company_service.get_company_by_id(uow, company_id)
        if company.owner_id == current_user.id:
            updated_company = await company_service.update_company(
                uow, company_id, company_update
            )
            logger.info(f"Updated company with ID: {company_id}")
            return updated_company
        else:
            raise UnAuthorizedException()
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
        company = await company_service.get_company_by_id(uow, company_id)
        if company.owner_id == current_user.id:
            deleted_company_id = await company_service.delete_company(uow, company_id)
            logger.info(f"Deleted company with ID: {deleted_company_id}")
            return {"status_code": 200}
        else:
            raise UnAuthorizedException()
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
        company = await company_service.get_company_by_id(uow, company_id)
        if company.owner_id == current_user.id:
            updated_company = await company_service.change_company_visibility(
                uow, company_id, is_visible
            )
            logger.info(f"Changed visibility for company with ID: {company_id}")
            return updated_company
        else:
            raise UnAuthorizedException()
    except Exception as e:
        logger.error(f"Error changing visibility for company with ID {company_id}: {e}")
        raise UpdatingException()
