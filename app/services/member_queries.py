from app.schemas.member import MembersListResponse, MemberBase
from app.uow.unitofwork import IUnitOfWork
from app.exceptions.base import NotFoundException
from app.core.logger import logger


class MemberQueries:

    @staticmethod
    async def get_members(
        uow: IUnitOfWork, company_id: int, skip: int = 0, limit: int = 10
    ) -> MembersListResponse:
        """
        Get a paginated list of members in a company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            company_id (int): The ID of the company.
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
                return MembersListResponse(
                    members=[MemberBase(**member.__dict__) for member in members],
                    total=len(members),
                )
        except Exception as e:
            logger.error(f"Error fetching members for company {company_id}: {e}")
            raise

    @staticmethod
    async def get_member_by_id(uow: IUnitOfWork, member_id: int) -> MemberBase:
        """
        Get a member by their ID.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            member_id (int): The ID of the member.

        Returns:
            MemberBase: The details of the member.

        Raises:
            NotFoundException: If the member with the given ID is not found.
            Exception: If there is an issue retrieving the member.
        """
        try:
            async with uow:
                member = await uow.member.find_one(id=member_id)
                if not member:
                    logger.error(f"Member with ID {member_id} not found")
                    raise NotFoundException()
                return MemberBase(**member.__dict__)
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error fetching member with ID {member_id}: {e}")
            raise
