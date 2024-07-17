from app.schemas.company import (
    CompanyCreate,
    CompanyDetail,
    CompanyUpdate,
    CompaniesListResponse,
    CompanyBase,
)
from app.uow.unitofwork import IUnitOfWork


class CompanyService:
    @staticmethod
    async def add_company(
        uow: IUnitOfWork, company: CompanyCreate, owner_id: int
    ) -> CompanyDetail:
        async with uow:
            company_dict = company.model_dump()
            company_dict["owner_id"] = owner_id

            company_model = await uow.company.add_one(company_dict)
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
                owner_id=current_user_id
            )

            combined_companies = list(
                {
                    company.id: company
                    for company in (visible_companies + user_companies)
                }.values()
            )

            paginated_companies = combined_companies[skip : skip + limit]

            company_list = CompaniesListResponse(
                companies=[
                    CompanyBase(**company.__dict__) for company in paginated_companies
                ],
                total=len(combined_companies),
            )
            return company_list

    @staticmethod
    async def get_company_by_id(uow: IUnitOfWork, company_id: int) -> CompanyDetail:
        async with uow:
            company_model = await uow.company.find_one(id=company_id)
            if company_model:
                return CompanyDetail(**company_model.__dict__)

    @staticmethod
    async def update_company(
        uow: IUnitOfWork, company_id: int, company_update: CompanyUpdate
    ) -> CompanyDetail:
        async with uow:
            company_dict = company_update.model_dump()

            await uow.company.edit_one(company_id, company_dict)
            await uow.commit()
            updated_company = await uow.company.find_one(id=company_id)
            return CompanyDetail(**updated_company.__dict__)

    @staticmethod
    async def delete_company(uow: IUnitOfWork, company_id: int) -> int:
        async with uow:
            deleted_company_id = await uow.company.delete_one(company_id)
            await uow.commit()
            return deleted_company_id

    @staticmethod
    async def change_company_visibility(
        uow: IUnitOfWork, company_id: int, is_visible: bool
    ) -> CompanyDetail:
        async with uow:
            company_model = await uow.company.find_one(id=company_id)
            if not company_model:
                raise ValueError("Company not found")

            # Update the attributes directly
            company_model.is_visible = is_visible

            # Save the changes
            await uow.company.edit_one(
                company_id,
                {
                    "is_visible": company_model.is_visible,
                },
            )
            await uow.commit()

            # Return updated company details
            return CompanyDetail(**company_model.__dict__)
