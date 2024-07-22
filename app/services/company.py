from app.core.logger import logger
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException
from app.schemas.company import (
    CompaniesListResponse,
    CompanyBase,
    CompanyCreate,
    CompanyDetail,
    CompanyUpdate,
)
from app.schemas.member import MemberCreate
from app.uow.unitofwork import IUnitOfWork


class CompanyService:
    @staticmethod
    async def add_company(
        uow: IUnitOfWork, company: CompanyCreate, owner_id: int
    ) -> CompanyDetail:
        """
        Add a new company and set the owner as a member.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            company (CompanyCreate): The company data to add.
            owner_id (int): The ID of the user who owns the company.

        Returns:
            CompanyDetail: The details of the newly added company.

        Raises:
            UnAuthorizedException: If the owner is already a member of another company.
        """
        async with uow:
            await CompanyService._validate_owner(uow, owner_id)

            company_dict = company.model_dump()
            company_dict["owner_id"] = owner_id
            company_model = await uow.company.add_one(company_dict)

            await CompanyService._assign_owner_as_member(
                uow, owner_id, company_model.id
            )

            await uow.commit()
            return CompanyDetail(**company_model.__dict__)

    @staticmethod
    async def get_companies(
        uow: IUnitOfWork, current_user_id: int, skip: int = 0, limit: int = 10
    ) -> CompaniesListResponse:
        """
        Retrieve a list of companies visible to the current user and owned by them.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            current_user_id (int): The ID of the current user.
            skip (int): The number of companies to skip (pagination).
            limit (int): The maximum number of companies to return (pagination).

        Returns:
            CompaniesListResponse: The list of companies and total count.
        """
        async with uow:
            visible_companies = await uow.company.find_all_visible(
                skip=skip, limit=limit
            )
            user_companies = await uow.company.find_all_by_owner(
                owner_id=current_user_id, skip=skip, limit=limit
            )

            combined_companies = CompanyService._merge_and_paginate_companies(
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
        """
        Get details of a company by its ID.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            company_id (int): The ID of the company to retrieve.

        Returns:
            CompanyDetail: The details of the company.

        Raises:
            NotFoundException: If the company with the given ID does not exist.
        """
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
        """
        Update a company's details.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            company_id (int): The ID of the company to update.
            current_user_id (int): The ID of the current user.
            company_update (CompanyUpdate): The data to update.

        Returns:
            CompanyDetail: The updated company details.

        Raises:
            UnAuthorizedException: If the current user is not the owner of the company.
        """
        async with uow:
            await CompanyService._ensure_ownership(uow, company_id, current_user_id)
            await uow.company.edit_one(company_id, company_update.model_dump())
            await uow.commit()

            updated_company = await uow.company.find_one(id=company_id)
            return CompanyDetail(**updated_company.__dict__)

    @staticmethod
    async def delete_company(
        uow: IUnitOfWork, company_id: int, current_user_id: int
    ) -> int:
        """
        Delete a company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            company_id (int): The ID of the company to delete.
            current_user_id (int): The ID of the current user.

        Returns:
            int: The ID of the deleted company.

        Raises:
            UnAuthorizedException: If the current user is not the owner of the company.
        """
        async with uow:
            await CompanyService._ensure_ownership(uow, company_id, current_user_id)
            deleted_company = await uow.company.delete_one(company_id)
            await uow.commit()
            return deleted_company.id

    @staticmethod
    async def change_company_visibility(
        uow: IUnitOfWork, company_id: int, current_user_id: int, is_visible: bool
    ) -> CompanyDetail:
        """
        Change the visibility of a company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            company_id (int): The ID of the company.
            current_user_id (int): The ID of the current user.
            is_visible (bool): The new visibility status.

        Returns:
            CompanyDetail: The company details after updating visibility.

        Raises:
            UnAuthorizedException: If the current user is not the owner of the company.
            ValueError: If the company is not found.
        """
        async with uow:
            await CompanyService._ensure_ownership(uow, company_id, current_user_id)
            company_model = await uow.company.find_one(id=company_id)
            if not company_model:
                logger.warning(f"Company with ID {company_id} not found")
                raise ValueError("Company not found")

            company_model.is_visible = is_visible
            await uow.company.edit_one(company_id, {"is_visible": is_visible})
            await uow.commit()

            return CompanyDetail(**company_model.__dict__)

    @staticmethod
    def _merge_and_paginate_companies(visible_companies, user_companies, skip, limit):
        """
        Combine visible companies and user-owned companies, and paginate the results.

        Args:
            visible_companies (list): The list of visible companies.
            user_companies (list): The list of companies owned by the user.
            skip (int): The number of companies to skip.
            limit (int): The maximum number of companies to return.

        Returns:
            dict: A dictionary containing paginated companies and total count.
        """
        combined_companies = list(
            {
                company.id: company for company in (visible_companies + user_companies)
            }.values()
        )
        paginated_companies = combined_companies[skip : skip + limit]
        return {"paginated": paginated_companies, "total": len(combined_companies)}

    @staticmethod
    async def _ensure_ownership(uow: IUnitOfWork, company_id: int, user_id: int):
        """
        Ensure the current user is the owner of the company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            company_id (int): The ID of the company.
            user_id (int): The ID of the current user.

        Returns:
            CompanyDetail: The company details.

        Raises:
            UnAuthorizedException: If the current user is not the owner of the company.
        """
        company = await CompanyService.get_company_by_id(uow, company_id)
        if company.owner_id != user_id:
            logger.error(
                f"User {user_id} is not authorized to access company {company_id}"
            )
            raise UnAuthorizedException()
        return company

    @staticmethod
    async def _validate_owner(uow: IUnitOfWork, owner_id: int):
        """
        Validate if the owner is already a member of another company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            owner_id (int): The ID of the user who is supposed to be the owner.

        Raises:
            UnAuthorizedException: If the owner is already a member of another company.
        """
        existing_member = await uow.member.find_one(user_id=owner_id)
        if existing_member:
            logger.error(f"User {owner_id} is already a member of another company")
            raise UnAuthorizedException()

    @staticmethod
    async def _assign_owner_as_member(uow: IUnitOfWork, owner_id: int, company_id: int):
        """
        Add the owner as a member of the newly created company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            owner_id (int): The ID of the owner.
            company_id (int): The ID of the company.
        """
        member_data = MemberCreate(user_id=owner_id, company_id=company_id, role=1)
        await uow.member.add_one(member_data.model_dump(exclude={"id"}))
