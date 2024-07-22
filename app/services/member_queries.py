from app.schemas.member import MembersListResponse, MemberBase
from app.uow.unitofwork import IUnitOfWork


class MemberQueries:

    @staticmethod
    async def get_members(
        uow: IUnitOfWork, company_id: int, skip: int = 0, limit: int = 10
    ) -> MembersListResponse:
        """
        Get a paginated list of members in a company.
        """
        async with uow:
            members = await uow.member.find_all_by_company(
                company_id=company_id, skip=skip, limit=limit
            )
            return MembersListResponse(
                members=[MemberBase(**member.__dict__) for member in members],
                total=len(members),
            )

    @staticmethod
    async def get_member_by_id(uow: IUnitOfWork, member_id: int) -> MemberBase:
        """
        Get a member by their ID.
        """
        async with uow:
            member = await uow.member.find_one(id=member_id)
            return MemberBase(**member.__dict__)
