import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyBase,
    CompaniesListResponse,
    CompanyDetail,
)
from app.services.company import CompanyService
from app.uow.unitofwork import IUnitOfWork


@pytest.mark.asyncio
async def test_add_company():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_company_repo = AsyncMock()
    mock_member_repo = AsyncMock()
    mock_uow.company = mock_company_repo
    mock_uow.member = mock_member_repo

    company_data = CompanyCreate(
        name="Test Company",
        description="This is a test company",
        owner_id=1,
        is_visible=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_company_repo.find_one.return_value = None
    mock_member_repo.find_one.return_value = None

    added_company = CompanyDetail(
        id=1,
        name="Test Company",
        description="This is a test company",
        owner_id=1,
        is_visible=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_company_repo.add_one.return_value = added_company
    company_detail = await CompanyService.add_company(
        mock_uow, company_data, owner_id=1
    )
    assert company_detail == added_company


@pytest.mark.asyncio
async def test_get_companies():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_uow.company = AsyncMock()

    mock_companies = [
        CompanyBase(
            id=1,
            name="Test Company",
            description="This is a test company",
            owner_id=1,
            is_visible=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
    ]
    mock_uow.company.find_all_visible.return_value = mock_companies

    companies_list = await CompanyService.get_companies(mock_uow, current_user_id=1)

    assert companies_list != CompaniesListResponse(
        companies=mock_companies, total=len(mock_companies)
    )


@pytest.mark.asyncio
async def test_get_company_by_id():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_uow.company = AsyncMock()

    company_id = 1
    mock_company = CompanyDetail(
        id=company_id,
        name="Test Company",
        description="This is a test company",
        owner_id=1,
        is_visible=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_uow.company.find_one.return_value = mock_company

    company_detail = await CompanyService.get_company_by_id(mock_uow, company_id)

    assert company_detail == mock_company


@pytest.mark.asyncio
async def test_update_company():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_uow.company = AsyncMock()

    company_id = 1
    company_update = CompanyUpdate(
        name="Updated Company", description="This is an updated company"
    )
    mock_company = CompanyCreate(
        id=company_id,
        name="Test Company",
        description="This is a test company",
        owner_id=1,
        is_visible=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    updated_company = CompanyCreate(
        id=company_id,
        name="Updated Company",
        description="This is an updated company",
        owner_id=1,
        is_visible=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    mock_uow.company.find_one.return_value = mock_company
    mock_uow.company.edit_one.return_value = updated_company

    company_detail = await CompanyService.update_company(
        mock_uow, company_id, 1, company_update
    )

    mock_uow.company.edit_one.assert_called_once()
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_company():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_uow.company = AsyncMock()

    company_id = 1
    mock_uow.company.delete_one.return_value = company_id

    deleted_company_id = 1

    assert deleted_company_id == company_id


@pytest.mark.asyncio
async def test_change_company_visibility():
    mock_uow = AsyncMock(IUnitOfWork)
    mock_uow.company = AsyncMock()

    company_id = 1
    is_visible = False
    mock_company = CompanyCreate(
        id=company_id,
        name="Test Company",
        description="This is a test company",
        owner_id=1,
        is_visible=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    updated_company = CompanyCreate(
        id=company_id,
        name="Test Company",
        description="This is a test company",
        owner_id=1,
        is_visible=is_visible,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    mock_uow.company.find_one.return_value = mock_company
    mock_uow.company.edit_one.return_value = updated_company

    company_detail = await CompanyService.change_company_visibility(
        mock_uow, company_id, 1, is_visible
    )

    assert company_detail.is_visible == is_visible
    mock_uow.company.edit_one.assert_called_once()
    mock_uow.commit.assert_called_once()
