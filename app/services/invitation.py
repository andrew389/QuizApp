from fastapi import Request

from app.core.logger import logger
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException
from app.schemas.invitation import (
    InvitationBase,
    SendInvitation,
    InvitationResponse,
    InvitationsListResponse,
)
from app.schemas.member import MemberCreate
from app.uow.unitofwork import IUnitOfWork
from app.utils.role import Role
from app.utils.user import get_pagination_urls


class InvitationService:

    @staticmethod
    async def send_invitation(
        uow: IUnitOfWork,
        invitation_data: SendInvitation,
        sender_id: int,
        company_id: int,
    ) -> InvitationBase:
        """
        Send an invitation from a user to another user to join a company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            invitation_data (SendInvitation): The invitation data.
            sender_id (int): The ID of the user sending the invitation.
            company_id (int): The ID of the company to which the invitation is sent.

        Returns:
            InvitationBase: The details of the created invitation.

        Raises:
            UnAuthorizedException: If the sender is not authorized.
            Exception: If the receiver is already a member of the company.
        """
        async with uow:
            await InvitationService._validate_sender(uow, sender_id, company_id)
            await InvitationService._check_existing_member(
                uow, invitation_data.receiver_id, company_id
            )

            invitation_dict = invitation_data.model_dump()
            invitation_dict.update(
                {
                    "sender_id": sender_id,
                    "company_id": company_id,
                }
            )

            invitation = await uow.invitation.add_one(invitation_dict)

            invitation_data = {
                key: value
                for key, value in invitation.__dict__.items()
                if not key.startswith("_")
            }

            return InvitationBase.model_validate(invitation_data)

    @staticmethod
    async def get_invitations(
        uow: IUnitOfWork, user_id: int, request: Request, skip: int = 0, limit: int = 10
    ) -> InvitationsListResponse:
        """
        Retrieve a list of invitations received by the user.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            user_id (int): The ID of the user.
            request (Request): request from endpoint to get base url.
            skip (int): Number of invitations to skip (pagination).
            limit (int): Maximum number of invitations to return (pagination).

        Returns:
            InvitationsListResponse: The list of received invitations and total count.
        """
        async with uow:
            invitations = await uow.invitation.find_all_by_receiver(
                receiver_id=user_id, skip=skip, limit=limit
            )
            total_invitations = await uow.invitation.count_all_by_receiver(
                receiver_id=user_id
            )
            links = get_pagination_urls(request, skip, limit, total_invitations)

            return InvitationsListResponse(
                links=links,
                invitations=[
                    InvitationBase(**invitation.__dict__) for invitation in invitations
                ],
                total=total_invitations,
            )

    @staticmethod
    async def get_sent_invitations(
        uow: IUnitOfWork, user_id: int, request: Request, skip: int = 0, limit: int = 10
    ) -> InvitationsListResponse:
        """
        Retrieve a list of invitations sent by the user.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            user_id (int): The ID of the user.
            request (Request): request from endpoint to get base url.
            skip (int): Number of invitations to skip (pagination).
            limit (int): Maximum number of invitations to return (pagination).

        Returns:
            InvitationsListResponse: The list of sent invitations and total count.
        """
        async with uow:
            invitations = await uow.invitation.find_all_by_sender(
                sender_id=user_id, skip=skip, limit=limit
            )

            total_invitations = await uow.invitation.count_all_by_sender(
                sender_id=user_id
            )
            links = get_pagination_urls(request, skip, limit, total_invitations)

            return InvitationsListResponse(
                links=links,
                invitations=[
                    InvitationBase(**invitation.__dict__) for invitation in invitations
                ],
                total=total_invitations,
            )

    @staticmethod
    async def cancel_invitation(
        uow: IUnitOfWork, invitation_id: int, sender_id: int
    ) -> int:
        """
        Cancel a specific invitation.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            invitation_id (int): The ID of the invitation to cancel.
            sender_id (int): The ID of the user canceling the invitation.

        Returns:
            int: The ID of the cancelled invitation.

        Raises:
            UnAuthorizedException: If the sender is not authorized.
            NotFoundException: If the invitation is not found.
        """
        async with uow:
            invitation = await InvitationService._get_invitation(uow, invitation_id)
            await InvitationService._validate_sender(
                uow, sender_id, invitation.company_id
            )
            InvitationService._validate_pending_status(invitation)

            cancelled_invitation = await uow.invitation.delete_one(invitation_id)

            return cancelled_invitation.id

    @staticmethod
    async def accept_invitation(
        uow: IUnitOfWork, invitation_id: int, receiver_id: int
    ) -> InvitationResponse:
        """
        Accept a specific invitation and add the user as a member.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            invitation_id (int): The ID of the invitation to accept.
            receiver_id (int): The ID of the user accepting the invitation.

        Returns:
            InvitationResponse: The details of the accepted invitation.

        Raises:
            UnAuthorizedException: If the receiver is not authorized or the invitation status is incorrect.
            NotFoundException: If the invitation is not found.
        """
        async with uow:
            invitation = await InvitationService._get_invitation(uow, invitation_id)
            InvitationService._validate_receiver(invitation, receiver_id)
            InvitationService._validate_pending_status(invitation)

            member_data = MemberCreate(
                user_id=receiver_id,
                company_id=invitation.company_id,
                role=Role.MEMBER.value,
            )
            await uow.member.add_one(member_data.model_dump(exclude={"id"}))
            await uow.invitation.edit_one(invitation_id, {"status": "accepted"})

            return await InvitationService._build_invitation_response(
                uow, invitation, receiver_id, "accepted"
            )

    @staticmethod
    async def decline_invitation(
        uow: IUnitOfWork, invitation_id: int, receiver_id: int
    ) -> InvitationResponse:
        """
        Decline a specific invitation.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            invitation_id (int): The ID of the invitation to decline.
            receiver_id (int): The ID of the user declining the invitation.

        Returns:
            InvitationResponse: The details of the declined invitation.

        Raises:
            UnAuthorizedException: If the receiver is not authorized or the invitation status is incorrect.
            NotFoundException: If the invitation is not found.
        """
        async with uow:
            invitation = await InvitationService._get_invitation(uow, invitation_id)
            InvitationService._validate_receiver(invitation, receiver_id)
            InvitationService._validate_pending_status(invitation)

            await uow.invitation.edit_one(invitation_id, {"status": "declined"})
            await uow.commit()

            return await InvitationService._build_invitation_response(
                uow, invitation, receiver_id, "declined"
            )

    @staticmethod
    async def _get_invitation(uow: IUnitOfWork, invitation_id: int):
        """
        Retrieve an invitation by its ID.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            invitation_id (int): The ID of the invitation to retrieve.

        Returns:
            InvitationBase: The invitation details.

        Raises:
            NotFoundException: If the invitation is not found.
        """
        invitation = await uow.invitation.find_one(id=invitation_id)

        if not invitation:
            logger.error(f"Invitation with ID {invitation_id} not found")
            raise NotFoundException()

        return invitation

    @staticmethod
    async def _validate_sender(uow: IUnitOfWork, sender_id: int, company_id: int):
        """
        Validate if the sender is the owner of the company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            sender_id (int): The ID of the sender.
            company_id (int): The ID of the company.

        Raises:
            UnAuthorizedException: If the sender is not the owner.
        """
        owner = await uow.member.find_owner(user_id=sender_id, company_id=company_id)

        if not owner:
            logger.error(
                f"User {sender_id} is not authorized to send invitations for company {company_id}"
            )
            raise UnAuthorizedException()

    @staticmethod
    async def _check_existing_member(uow: IUnitOfWork, user_id: int, company_id: int):
        """
        Check if the user is already a member of the company.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            user_id (int): The ID of the user.
            company_id (int): The ID of the company.

        Raises:
            Exception: If the user is already a member.
        """
        existing_member = await uow.member.find_one(
            user_id=user_id, company_id=company_id
        )

        if existing_member:
            logger.error(f"User {user_id} is already a member of company {company_id}")
            raise Exception("User is already a member of the company")

    @staticmethod
    def _validate_receiver(invitation, receiver_id: int):
        """
        Validate if the user is the receiver of the invitation.

        Args:
            invitation (InvitationBase): The invitation details.
            receiver_id (int): The ID of the receiver.

        Raises:
            UnAuthorizedException: If the receiver does not match the invitation receiver.
        """
        if invitation.receiver_id != receiver_id:
            logger.error(
                f"User {receiver_id} is not authorized to accept invitation ID {invitation.id}"
            )
            raise UnAuthorizedException()

    @staticmethod
    def _validate_pending_status(invitation):
        """
        Validate if the invitation is in pending status.

        Args:
            invitation (InvitationBase): The invitation details.

        Raises:
            UnAuthorizedException: If the invitation status is not pending.
        """
        if invitation.status != "pending":
            logger.error(
                f"Invitation ID {invitation.id} has already been accepted or declined"
            )
            raise UnAuthorizedException()

    @staticmethod
    async def _build_invitation_response(
        uow: IUnitOfWork, invitation, receiver_id: int, status: str
    ) -> InvitationResponse:
        """
        Build the response object for the invitation.

        Args:
            uow (IUnitOfWork): The unit of work for database transactions.
            invitation (InvitationBase): The invitation details.
            receiver_id (int): The ID of the receiver.
            status (str): The status of the invitation (accepted/declined).

        Returns:
            InvitationResponse: The constructed response object.
        """
        company = await uow.company.find_one(id=invitation.company_id)
        user = await uow.user.find_one(id=receiver_id)

        return InvitationResponse(
            title=invitation.title,
            description=invitation.description,
            company_name=company.name,
            receiver_email=user.email,
            status=status,
        )
