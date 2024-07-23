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


class InvitationService:
    @staticmethod
    async def send_invitation(
        uow: IUnitOfWork,
        invitation_data: SendInvitation,
        sender_id: int,
        company_id: int,
    ) -> InvitationBase:
        """
        Send an invitation to a user for a company.
        """
        async with uow:
            await InvitationService._get_owner(uow, sender_id, company_id)
            await InvitationService._check_existing_member(
                uow, invitation_data.receiver_id, company_id
            )

            invitation_dict = invitation_data.model_dump()
            invitation_dict.update({"sender_id": sender_id, "company_id": company_id})
            invitation = await uow.invitation.add_one(invitation_dict)
            await uow.commit()
            return InvitationBase(**invitation.__dict__)

    @staticmethod
    async def get_invitations(
        uow: IUnitOfWork, user_id: int, skip: int = 0, limit: int = 10
    ) -> InvitationsListResponse:
        """
        Get invitations received by the user.
        """
        async with uow:
            invitations = await uow.invitation.find_all_by_receiver(
                receiver_id=user_id, skip=skip, limit=limit
            )
            return InvitationsListResponse(
                invitations=[
                    InvitationBase(**invitation.__dict__) for invitation in invitations
                ],
                total=len(invitations),
            )

    @staticmethod
    async def get_sent_invitations(
        uow: IUnitOfWork, user_id: int, skip: int = 0, limit: int = 10
    ) -> InvitationsListResponse:
        """
        Get invitations sent by the user.
        """
        async with uow:
            invitations = await uow.invitation.find_all_by_sender(
                sender_id=user_id, skip=skip, limit=limit
            )
            return InvitationsListResponse(
                invitations=[
                    InvitationBase(**invitation.__dict__) for invitation in invitations
                ],
                total=len(invitations),
            )

    @staticmethod
    async def cancel_invitation(
        uow: IUnitOfWork, invitation_id: int, sender_id: int
    ) -> int:
        """
        Cancel a pending invitation.
        """
        async with uow:
            invitation = await InvitationService._get_invitation(uow, invitation_id)
            InvitationService._check_sender(invitation, sender_id)
            InvitationService._check_pending_status(invitation)

            cancelled_invitation = await uow.invitation.delete_one(invitation_id)
            await uow.commit()
            return cancelled_invitation.id

    @staticmethod
    async def accept_invitation(
        uow: IUnitOfWork, invitation_id: int, receiver_id: int
    ) -> InvitationResponse:
        """
        Accept a pending invitation.
        """
        async with uow:
            invitation = await InvitationService._get_invitation(uow, invitation_id)
            InvitationService._check_receiver(invitation, receiver_id)
            InvitationService._check_pending_status(invitation)

            member_data = MemberCreate(
                user_id=receiver_id,
                company_id=invitation.company_id,
                role=Role.MEMBER.value,
            )
            await uow.member.add_one(member_data.model_dump(exclude={"id"}))
            await uow.invitation.edit_one(invitation_id, {"status": "accepted"})
            await uow.commit()

            return await InvitationService._build_invitation_response(
                uow, invitation, receiver_id, "accepted"
            )

    @staticmethod
    async def decline_invitation(
        uow: IUnitOfWork, invitation_id: int, receiver_id: int
    ) -> InvitationResponse:
        """
        Decline a pending invitation.
        """
        async with uow:
            invitation = await InvitationService._get_invitation(uow, invitation_id)
            InvitationService._check_receiver(invitation, receiver_id)
            InvitationService._check_pending_status(invitation)

            await uow.invitation.edit_one(invitation_id, {"status": "declined"})
            await uow.commit()

            return await InvitationService._build_invitation_response(
                uow, invitation, receiver_id, "declined"
            )

    @staticmethod
    async def _get_owner(uow: IUnitOfWork, user_id: int, company_id: int):
        """
        Verify that the user is the owner of the company.
        """
        owner = await uow.member.find_owner(user_id=user_id, company_id=company_id)
        if not owner:
            logger.error("Only the owner can send invitations")
            raise UnAuthorizedException()
        return owner

    @staticmethod
    async def _check_existing_member(uow: IUnitOfWork, user_id: int, company_id: int):
        """
        Check if the user is already a member of the company.
        """
        existing_member = await uow.member.find_one(
            user_id=user_id, company_id=company_id
        )
        if existing_member:
            logger.error("User already works in the company")
            raise Exception("User is already a member of the company")

    @staticmethod
    async def _get_invitation(uow: IUnitOfWork, invitation_id: int):
        """
        Retrieve an invitation by ID.
        """
        invitation = await uow.invitation.find_one(id=invitation_id)
        if not invitation:
            logger.error("Invitation not found")
            raise NotFoundException()
        return invitation

    @staticmethod
    def _check_sender(invitation, sender_id: int):
        """
        Verify that the sender is the one trying to cancel the invitation.
        """
        if invitation.sender_id != sender_id:
            logger.error("Only the sender can cancel the invitation")
            raise UnAuthorizedException()

    @staticmethod
    def _check_receiver(invitation, receiver_id: int):
        """
        Verify that the receiver is the one trying to act on the invitation.
        """
        if invitation.receiver_id != receiver_id:
            logger.error("Unauthorized action")
            raise UnAuthorizedException()

    @staticmethod
    def _check_pending_status(invitation):
        """
        Ensure the invitation is still pending.
        """
        if invitation.status != "pending":
            logger.error("Invitation has already been accepted or declined")
            raise UnAuthorizedException()

    @staticmethod
    async def _build_invitation_response(
        uow: IUnitOfWork, invitation, receiver_id: int, status: str
    ):
        """
        Build the response for an invitation action.
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
