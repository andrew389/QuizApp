from app.core.logger import logger
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException
from app.schemas.member import MemberCreate, AdminsListResponse, MemberBase
from app.uow.unitofwork import IUnitOfWork
from app.utils.role import Role


class MemberManagement:
    @staticmethod
    async def add_member(uow: IUnitOfWork, user_id: int, company_id: int):
        """
        Add a new member to the company.
        """
        member_data = MemberCreate(
            user_id=user_id, company_id=company_id, role=Role.MEMBER.value
        )
        await uow.member.add_one(member_data.model_dump(exclude={"id"}))

    @staticmethod
    async def remove_member(
        uow: IUnitOfWork, user_id: int, member_id: int
    ) -> MemberBase:
        """
        Remove a member from the company.
        """
        async with uow:
            member = await uow.member.find_one(user_id=member_id)
            await MemberManagement._validate_member_for_remove(
                uow, member, user_id, member_id
            )
            updated_member = await uow.member.edit_one(
                member_id, {"role": Role.UNEMPLOYED.value, "company_id": None}
            )
            await uow.commit()
            return updated_member

    @staticmethod
    async def _validate_member_for_remove(
        uow: IUnitOfWork, member, user_id: int, member_id: int
    ):
        """
        Validate conditions for removing a member.
        """
        owner = await uow.member.find_one(user_id=user_id)

        if owner.role not in [Role.OWNER.value]:
            raise UnAuthorizedException()

        if not member:
            logger.error("Member not found")
            raise NotFoundException()

        if member.role == Role.OWNER.value:
            logger.error("You can't remove owner")
            raise UnAuthorizedException()

        if user_id == member_id:
            logger.error("You can't remove yourself")
            raise UnAuthorizedException()

    @staticmethod
    async def leave_company(
        uow: IUnitOfWork, user_id: int, company_id: int
    ) -> MemberBase:
        """
        Allow a member to leave the company.
        """
        async with uow:
            member = await uow.member.find_one(user_id=user_id, company_id=company_id)
            MemberManagement._validate_member_for_leave(member)
            updated_member = await uow.member.edit_one(
                member.id, {"role": Role.UNEMPLOYED.value, "company_id": None}
            )
            await uow.commit()
            return updated_member

    @staticmethod
    def _validate_member_for_leave(member):
        """
        Validate conditions for leaving a company.
        """
        if not member or member.role == Role.OWNER.value:
            logger.error("Leaving exception")
            raise UnAuthorizedException()

    @staticmethod
    async def appoint_admin(
        uow: IUnitOfWork, owner_id: int, company_id: int, member_id: int
    ) -> MemberBase:
        """
        Appoint a member as an admin.
        """
        from app.services.member_requests import MemberRequests

        async with uow:
            await MemberRequests.validate_owner(uow, owner_id, company_id)
            member = await uow.member.find_one(user_id=member_id)
            if not member or member.role != Role.MEMBER.value:
                logger.error("Member not found or not eligible")
                raise NotFoundException()

            updated_member = await uow.member.edit_one(
                member_id, {"role": Role.ADMIN.value}
            )
            await uow.commit()
            return MemberBase(**updated_member.__dict__)

    @staticmethod
    async def remove_admin(
        uow: IUnitOfWork, owner_id: int, company_id: int, member_id: int
    ) -> MemberBase:
        """
        Remove an admin role from a member.
        """
        from app.services.member_requests import MemberRequests

        async with uow:
            await MemberRequests.validate_owner(uow, owner_id, company_id)
            member = await uow.member.find_one(user_id=member_id)
            if not member or member.role != Role.ADMIN.value:
                logger.error("Admin not found or not eligible")
                raise NotFoundException()

            updated_member = await uow.member.edit_one(
                member_id, {"role": Role.MEMBER.value}
            )
            await uow.commit()
            return MemberBase(**updated_member.__dict__)

    @staticmethod
    async def get_admins(
        uow: IUnitOfWork, company_id: int, skip: int = 0, limit: int = 10
    ) -> AdminsListResponse:
        """
        Get a list of admins for a company.
        """
        async with uow:
            admins = await uow.member.find_all_by_company_and_role(
                company_id=company_id, role=Role.ADMIN.value, skip=skip, limit=limit
            )
            return AdminsListResponse(
                admins=[MemberBase(**admin.__dict__) for admin in admins],
                total=len(admins),
            )
