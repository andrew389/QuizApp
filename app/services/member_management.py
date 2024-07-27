from app.core.logger import logger
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException
from app.schemas.member import MemberCreate, AdminsListResponse, MemberBase
from app.uow.unitofwork import IUnitOfWork
from app.utils.role import Role


class MemberManagement:

    @staticmethod
    async def add_member(uow: IUnitOfWork, user_id: int, company_id: int) -> MemberBase:
        """
        Add a new member to the company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            user_id (int): The ID of the user to add.
            company_id (int): The ID of the company.

        Returns:
            MemberBase: The details of the newly added member.

        Raises:
            Exception: If the member cannot be added.
        """
        member_data = MemberCreate(
            user_id=user_id, company_id=company_id, role=Role.MEMBER.value
        )
        try:
            member = await uow.member.add_one(member_data.model_dump(exclude={"id"}))

            member_data = {
                key: value
                for key, value in member.__dict__.items()
                if not key.startswith("_")
            }

            return MemberBase.model_validate(member_data)
        except Exception as e:
            logger.error(f"Error adding member {user_id} to company {company_id}: {e}")
            raise

    @staticmethod
    async def remove_member(
        uow: IUnitOfWork, user_id: int, member_id: int
    ) -> MemberBase:
        """
        Remove a member from the company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            user_id (int): The ID of the user performing the action.
            member_id (int): The ID of the member to remove.

        Returns:
            MemberBase: The details of the removed member.

        Raises:
            UnAuthorizedException: If the user does not have permission to remove the member.
            NotFoundException: If the member or user is not found.
        """
        async with uow:
            member = await uow.member.find_one(user_id=member_id)

            await MemberManagement._validate_member_for_remove(
                uow, member, user_id, member_id
            )

            updated_member = await uow.member.edit_one(
                member_id, {"role": Role.UNEMPLOYED.value, "company_id": None}
            )

            member_data = {
                key: value
                for key, value in updated_member.__dict__.items()
                if not key.startswith("_")
            }

            return MemberBase.model_validate(member_data)

    @staticmethod
    async def _validate_member_for_remove(
        uow: IUnitOfWork, member, user_id: int, member_id: int
    ):
        """
        Validate conditions for removing a member.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            member (MemberBase): The member to be removed.
            user_id (int): The ID of the user performing the action.
            member_id (int): The ID of the member to remove.

        Raises:
            UnAuthorizedException: If the user does not have permission to remove the member.
            NotFoundException: If the member is not found.
        """
        owner_or_admin = await uow.member.find_one(user_id=user_id)

        if owner_or_admin.role not in [Role.OWNER.value, Role.ADMIN.value]:
            logger.error(
                f"User {user_id} is not authorized to remove member {member_id}"
            )
            raise UnAuthorizedException()

        if not member:
            logger.error(f"Member with ID {member_id} not found")
            raise NotFoundException()

        if member.role == Role.OWNER.value:
            logger.error(f"Cannot remove owner with ID {member_id}")
            raise UnAuthorizedException()

        if user_id == member_id:
            logger.error(f"User cannot remove themselves")
            raise UnAuthorizedException()

    @staticmethod
    async def leave_company(
        uow: IUnitOfWork, user_id: int, company_id: int
    ) -> MemberBase:
        """
        Allow a member to leave the company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            user_id (int): The ID of the user leaving the company.
            company_id (int): The ID of the company.

        Returns:
            MemberBase: The details of the updated member.

        Raises:
            UnAuthorizedException: If the user is not authorized or is an owner.
            NotFoundException: If the member is not found.
        """
        async with uow:
            member = await uow.member.find_one(user_id=user_id, company_id=company_id)

            MemberManagement._validate_member_for_leave(member)

            updated_member = await uow.member.edit_one(
                member.id, {"role": Role.UNEMPLOYED.value, "company_id": None}
            )

            member_data = {
                key: value
                for key, value in updated_member.__dict__.items()
                if not key.startswith("_")
            }

            return MemberBase.model_validate(member_data)

    @staticmethod
    def _validate_member_for_leave(member):
        """
        Validate conditions for leaving a company.

        Args:
            member (MemberBase): The member attempting to leave.

        Raises:
            UnAuthorizedException: If the member is not found or is an owner.
        """
        if not member or member.role == Role.OWNER.value:
            logger.error(f"Member is either not found or an owner, cannot leave")
            raise UnAuthorizedException()

    @staticmethod
    async def appoint_admin(
        uow: IUnitOfWork, owner_id: int, company_id: int, member_id: int
    ) -> MemberBase:
        """
        Appoint a member as an admin.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            owner_id (int): The ID of the owner performing the action.
            company_id (int): The ID of the company.
            member_id (int): The ID of the member to promote.

        Returns:
            MemberBase: The details of the updated member.

        Raises:
            NotFoundException: If the member is not found or not eligible.
        """
        from app.services.member_requests import MemberRequests

        async with uow:
            await MemberRequests.validate_owner(uow, owner_id, company_id)
            member = await uow.member.find_one(user_id=member_id)
            if not member or member.role != Role.MEMBER.value:
                logger.error(
                    f"Member with ID {member_id} not found or not eligible to be an admin"
                )
                raise NotFoundException()

            updated_member = await uow.member.edit_one(
                member_id, {"role": Role.ADMIN.value}
            )

            member_data = {
                key: value
                for key, value in updated_member.__dict__.items()
                if not key.startswith("_")
            }

            return MemberBase.model_validate(member_data)

    @staticmethod
    async def remove_admin(
        uow: IUnitOfWork, owner_id: int, company_id: int, member_id: int
    ) -> MemberBase:
        """
        Remove an admin role from a member.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            owner_id (int): The ID of the owner performing the action.
            company_id (int): The ID of the company.
            member_id (int): The ID of the member to demote.

        Returns:
            MemberBase: The details of the updated member.

        Raises:
            NotFoundException: If the admin is not found or not eligible to be removed.
        """
        from app.services.member_requests import MemberRequests

        async with uow:
            await MemberRequests.validate_owner(uow, owner_id, company_id)
            member = await uow.member.find_one(user_id=member_id)

            if not member or member.role != Role.ADMIN.value:
                logger.error(
                    f"Admin with ID {member_id} not found or not eligible to be removed"
                )
                raise NotFoundException()

            updated_member = await uow.member.edit_one(
                member_id, {"role": Role.MEMBER.value}
            )

            member_data = {
                key: value
                for key, value in updated_member.__dict__.items()
                if not key.startswith("_")
            }

            return MemberBase.model_validate(member_data)

    @staticmethod
    async def check_is_user_have_permission(
        uow: IUnitOfWork, user_id: int, company_id: int
    ) -> bool:
        """
        Check if a user has permission to perform actions in a company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            user_id (int): The ID of the user.
            company_id (int): The ID of the company.

        Returns:
            bool: True if the user has permission, False otherwise.

        Raises:
            UnAuthorizedException: If the user does not have permission.
        """
        async with uow:
            member = await uow.member.find_one(user_id=user_id, company_id=company_id)

            if not member:
                logger.error(f"User {user_id} not found in company {company_id}")
                raise UnAuthorizedException()

            if member.role in [Role.OWNER.value, Role.ADMIN.value]:
                return True

            return False

    @staticmethod
    async def check_is_user_member_or_higher(
        uow: IUnitOfWork, user_id: int, company_id: int
    ) -> bool:
        """
        Check if a user is a member or has a higher role in the company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            user_id (int): The ID of the user.
            company_id (int): The ID of the company.

        Returns:
            bool: True if the user is a member or higher, False otherwise.

        Raises:
            UnAuthorizedException: If the user is not a member or higher.
        """
        async with uow:
            member = await uow.member.find_one(user_id=user_id, company_id=company_id)

            if not member:
                logger.error(f"User {user_id} is not a member of company {company_id}")
                raise UnAuthorizedException()
            return True
