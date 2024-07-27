from app.core.logger import logger
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException
from app.schemas.invitation import InvitationBase, SendInvitation, InvitationResponse
from app.schemas.member import MemberRequest
from app.uow.unitofwork import IUnitOfWork


class MemberRequests:

    @staticmethod
    async def request_to_join_company(
        uow: IUnitOfWork, user_id: int, request: MemberRequest, company_id: int
    ) -> InvitationBase:
        """
        Request to join a company by sending an invitation.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            user_id (int): The ID of the user requesting to join.
            request (MemberRequest): The request details.
            company_id (int): The ID of the company.

        Returns:
            InvitationBase: The created invitation.

        Raises:
            UnAuthorizedException: If the user is already a member of the company.
        """
        async with uow:
            if await MemberRequests._is_existing_member(uow, user_id, company_id):
                raise UnAuthorizedException()

            owner = await uow.company.find_one(id=company_id)

            invitation = await MemberRequests._create_invitation(
                uow, request, user_id, owner.owner_id, company_id
            )

            invitation_data = {
                key: value
                for key, value in invitation.__dict__.items()
                if not key.startswith("_")
            }

            return InvitationBase.model_validate(invitation_data)

    @staticmethod
    async def _is_existing_member(
        uow: IUnitOfWork, user_id: int, company_id: int
    ) -> bool:
        """
        Check if the user is already a member of the company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            user_id (int): The ID of the user.
            company_id (int): The ID of the company.

        Returns:
            bool: True if the user is a member, otherwise False.
        """
        existing_member = await uow.member.find_one(
            user_id=user_id, company_id=company_id
        )

        if existing_member:
            logger.error(f"User {user_id} is already a member of company {company_id}")
            return True

        return False

    @staticmethod
    async def _create_invitation(
        uow: IUnitOfWork,
        request: MemberRequest,
        user_id: int,
        receiver_id: int,
        company_id: int,
    ):
        """
        Create a new invitation with pending status.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            request (MemberRequest): The request details.
            user_id (int): The ID of the sender.
            receiver_id (int): The ID of the receiver.
            company_id (int): The ID of the company.

        Returns:
            dict: The created invitation.
        """
        invitation_data = SendInvitation(
            title=request.title,
            description=request.description,
            receiver_id=receiver_id,
            company_id=company_id,
        )
        invitation_dict = invitation_data.model_dump()

        invitation_dict.update(
            {"sender_id": user_id, "status": "pending", "company_id": company_id}
        )

        return await uow.invitation.add_one(invitation_dict)

    @staticmethod
    async def cancel_request_to_join(
        uow: IUnitOfWork, request_id: int, sender_id: int
    ) -> int:
        """
        Cancel a request to join a company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            request_id (int): The ID of the request.
            sender_id (int): The ID of the sender.

        Returns:
            int: The ID of the cancelled request.

        Raises:
            NotFoundException: If the invitation is not found.
            UnAuthorizedException: If the sender is not authorized to cancel the invitation.
        """
        async with uow:
            invitation = await uow.invitation.find_one(id=request_id)

            MemberRequests._validate_invitation_for_cancel(invitation, sender_id)

            cancelled_request = await uow.invitation.delete_one(request_id)

            return cancelled_request.id

    @staticmethod
    def _validate_invitation_for_cancel(invitation, sender_id):
        """
        Validate that the invitation can be cancelled.

        Args:
            invitation: The invitation object.
            sender_id (int): The ID of the sender.

        Raises:
            NotFoundException: If the invitation is not found.
            UnAuthorizedException: If the sender is not authorized to cancel the invitation.
        """
        if not invitation:
            logger.error("Invitation not found")
            raise NotFoundException()

        if invitation.sender_id != sender_id:
            logger.error("Only the sender can cancel the invitation")
            raise UnAuthorizedException()

        if invitation.status != "pending":
            logger.error("Invitation has already been accepted or declined")
            raise UnAuthorizedException()

    @staticmethod
    async def accept_request(
        uow: IUnitOfWork, owner_id: int, request_id: int
    ) -> InvitationResponse:
        """
        Accept a request to join a company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            owner_id (int): The ID of the owner accepting the request.
            request_id (int): The ID of the request.

        Returns:
            InvitationResponse: The response of the accepted invitation.

        Raises:
            NotFoundException: If the request is not found.
            UnAuthorizedException: If the request cannot be accepted.
        """
        from app.services.member_management import MemberManagement

        async with uow:
            request = await uow.invitation.find_one(id=request_id)

            MemberRequests._validate_request_for_accept(request)

            await MemberRequests.validate_owner(uow, owner_id, request.company_id)

            await uow.invitation.edit_one(request_id, {"status": "accepted"})

            await MemberManagement.add_member(
                uow, request.sender_id, request.company_id
            )

            return await MemberRequests._create_invitation_response(
                uow, request, "accepted"
            )

    @staticmethod
    def _validate_request_for_accept(request):
        """
        Validate that the request can be accepted.

        Args:
            request: The invitation request.

        Raises:
            NotFoundException: If the request is not found.
            UnAuthorizedException: If the request cannot be accepted.
        """
        if not request:
            logger.error("Request not found")
            raise NotFoundException()

        if request.status != "pending":
            logger.error("Invitation has already been accepted or declined")
            raise UnAuthorizedException()

    @staticmethod
    async def _create_invitation_response(
        uow: IUnitOfWork, request, status: str
    ) -> InvitationResponse:
        """
        Create a response for the invitation.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            request: The invitation request.
            status (str): The status of the invitation (accepted/declined).

        Returns:
            InvitationResponse: The response of the invitation.
        """
        company = await uow.company.find_one(id=request.company_id)

        user = await uow.user.find_one(id=request.receiver_id)

        return InvitationResponse(
            title=request.title,
            description=request.description,
            company_name=company.name,
            receiver_email=user.email,
            status=status,
        )

    @staticmethod
    async def decline_request(
        uow: IUnitOfWork, owner_id: int, request_id: int
    ) -> InvitationResponse:
        """
        Decline a request to join a company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            owner_id (int): The ID of the owner declining the request.
            request_id (int): The ID of the request.

        Returns:
            InvitationResponse: The response of the declined invitation.

        Raises:
            NotFoundException: If the request is not found.
            UnAuthorizedException: If the request cannot be declined.
        """
        async with uow:
            request = await uow.invitation.find_one(id=request_id)

            MemberRequests._validate_request_for_accept(request)

            await MemberRequests.validate_owner(uow, owner_id, request.company_id)

            await uow.invitation.edit_one(request_id, {"status": "declined"})

            return await MemberRequests._create_invitation_response(
                uow, request, "declined"
            )

    @staticmethod
    async def validate_owner(uow: IUnitOfWork, user_id: int, company_id: int):
        """
        Validate that the user is the owner of the company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            user_id (int): The ID of the user.
            company_id (int): The ID of the company.

        Raises:
            UnAuthorizedException: If the user is not the owner.
        """
        owner = await uow.member.find_owner(user_id=user_id, company_id=company_id)

        if not owner:
            logger.error(f"User {user_id} is not the owner of company {company_id}")
            raise UnAuthorizedException()
