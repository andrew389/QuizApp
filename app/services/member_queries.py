from fastapi import Request

from app.schemas.member import MembersListResponse, MemberBase, AdminsListResponse
from app.uow.unitofwork import IUnitOfWork
from app.exceptions.base import NotFoundException
from app.core.logger import logger
from app.utils.role import Role
from app.utils.user import get_pagination_urls, filter_data


class MemberQueries:

    @staticmethod
    async def get_members(
        uow: IUnitOfWork,
        company_id: int,
        request: Request,
        skip: int = 0,
        limit: int = 10,
    ) -> MembersListResponse:
        """
        Get a paginated list of members in a company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            company_id (int): The ID of the company.
            request (Request): request from endpoint to get base url.
            skip (int): Number of members to skip (pagination).
            limit (int): Maximum number of members to return (pagination).

        Returns:
            MembersListResponse: The list of members and the total count.

        Raises:
            Exception: If there is an issue retrieving members.
        """
        try:
            async with uow:
                members = await uow.member.find_all_by_company(
                    company_id=company_id, skip=skip, limit=limit
                )

                total_members = await uow.member.count_all_by_company(
                    company_id=company_id
                )

                links = get_pagination_urls(request, skip, limit, total_members)

                return MembersListResponse(
                    links=links,
                    members=[MemberBase(**member.__dict__) for member in members],
                    total=total_members,
                )
        except Exception as e:
            logger.error(f"Error fetching members for company {company_id}: {e}")
            raise

    @staticmethod
    async def get_admins(
        uow: IUnitOfWork,
        company_id: int,
        request: Request,
        skip: int = 0,
        limit: int = 10,
    ) -> AdminsListResponse:
        """
        Get a list of admins for a company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            company_id (int): The ID of the company.
            request (Request): request from endpoint to get base url.
            skip (int): Number of admins to skip (pagination).
            limit (int): Maximum number of admins to return (pagination).

        Returns:
            AdminsListResponse: The list of admins and total count.
        """
        async with uow:
            admins = await uow.member.find_all_by_company_and_role(
                company_id=company_id, role=Role.ADMIN.value, skip=skip, limit=limit
            )

            total_admins = await uow.member.count_all_by_company_and_role(
                company_id=company_id, role=Role.ADMIN.value
            )

            links = get_pagination_urls(request, skip, limit, total_admins)

            return AdminsListResponse(
                links=links,
                admins=[MemberBase(**admin.__dict__) for admin in admins],
                total=total_admins,
            )

    @staticmethod
    async def get_member_by_id(
        uow: IUnitOfWork, member_id: int, company_id: int
    ) -> MemberBase:
        """
        Get a member by their ID.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            member_id (int): The ID of the member.
            company_id (int): The ID of the company.

        Returns:
            MemberBase: The details of the member.

        Raises:
            NotFoundException: If the member with the given ID is not found.
            Exception: If there is an issue retrieving the member.
        """
        try:
            async with uow:
                member = await uow.member.find_one(id=member_id, company_id=company_id)

                if not member:
                    logger.error(f"Member with ID {member_id} not found")
                    raise NotFoundException()

                member_data = filter_data(member)

                return MemberBase.model_validate(member_data)
        except Exception as e:
            logger.error(f"Error fetching member with member_id {member_id}: {e}")
            raise
