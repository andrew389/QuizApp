from app.core.logger import logger
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException
from app.schemas.company import (
    CompanyCreate,
    CompanyDetail,
    CompanyUpdate,
    CompaniesListResponse,
    CompanyBase,
)
from app.schemas.member import MemberCreate
from app.uow.unitofwork import IUnitOfWork
from app.utils.role import Role


class CompanyService:
    @staticmethod
    async def add_company(
        uow: IUnitOfWork, company: CompanyCreate, owner_id: int
    ) -> CompanyDetail:
        async with uow:
            await CompanyService._check_existing_member(uow, owner_id)

            company_dict = company.model_dump()
            company_dict["owner_id"] = owner_id
            company_model = await uow.company.add_one(company_dict)

            await CompanyService._add_owner_as_member(uow, owner_id, company_model.id)

            await uow.commit()
            return CompanyDetail(**company_model.__dict__)

    @staticmethod
    async def get_companies(
        uow: IUnitOfWork, current_user_id: int, skip: int = 0, limit: int = 10
    ) -> CompaniesListResponse:
        async with uow:
            visible_companies = await uow.company.find_all_visible(
                skip=skip, limit=limit
            )
            user_companies = await uow.company.find_all_by_owner(
                owner_id=current_user_id, skip=skip, limit=limit
            )

            combined_companies = CompanyService._combine_and_paginate_companies(
                visible_companies, user_companies, skip, limit
            )

            return CompaniesListResponse(
                companies=[
                    CompanyBase(**company.__dict__)
                    for company in combined_companies["paginated"]
                ],
                total=combined_companies["total"],
            )

    @staticmethod
    async def get_company_by_id(uow: IUnitOfWork, company_id: int) -> CompanyDetail:
        async with uow:
            company_model = await uow.company.find_one(id=company_id)
            if not company_model:
                logger.warning(f"Company with ID {company_id} not found")
                raise NotFoundException()
            return CompanyDetail(**company_model.__dict__)

    @staticmethod
    async def update_company(
        uow: IUnitOfWork,
        company_id: int,
        current_user_id: int,
        company_update: CompanyUpdate,
    ) -> CompanyDetail:
        async with uow:
            await CompanyService.ensure_owner(uow, company_id, current_user_id)
            await uow.company.edit_one(company_id, company_update.model_dump())
            await uow.commit()

            updated_company = await uow.company.find_one(id=company_id)
            return CompanyDetail(**updated_company.__dict__)

    @staticmethod
    async def delete_company(
        uow: IUnitOfWork, company_id: int, current_user_id: int
    ) -> int:
        async with uow:
            await CompanyService.ensure_owner(uow, company_id, current_user_id)
            deleted_company = await uow.company.delete_one(company_id)
            await uow.commit()
            return deleted_company.id

    @staticmethod
    async def change_company_visibility(
        uow: IUnitOfWork, company_id: int, current_user_id: int, is_visible: bool
    ) -> CompanyDetail:
        async with uow:
            await CompanyService.ensure_owner(uow, company_id, current_user_id)
            company_model = await uow.company.find_one(id=company_id)
            if not company_model:
                raise ValueError("Company not found")

            company_model.is_visible = is_visible
            await uow.company.edit_one(company_id, {"is_visible": is_visible})
            await uow.commit()

            return CompanyDetail(**company_model.__dict__)

    @staticmethod
    def _combine_and_paginate_companies(visible_companies, user_companies, skip, limit):
        combined_companies = list(
            {
                company.id: company for company in (visible_companies + user_companies)
            }.values()
        )
        paginated_companies = combined_companies[skip : skip + limit]
        return {"paginated": paginated_companies, "total": len(combined_companies)}

    @staticmethod
    async def ensure_owner(uow: IUnitOfWork, company_id: int, user_id: int):
        company = await CompanyService.get_company_by_id(uow, company_id)
        if company.owner_id != user_id:
            raise UnAuthorizedException()
        return company

    @staticmethod
    async def _check_existing_member(uow: IUnitOfWork, owner_id: int):
        existing_member = await uow.member.find_one(user_id=owner_id)
        if existing_member:
            logger.error("User is already a member of another company")
            raise UnAuthorizedException()

    @staticmethod
    async def _add_owner_as_member(uow: IUnitOfWork, owner_id: int, company_id: int):
        member_data = MemberCreate(
            user_id=owner_id, company_id=company_id, role=Role.OWNER.value
        )
        await uow.member.add_one(member_data.model_dump(exclude={"id"}))
