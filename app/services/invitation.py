from datetime import datetime
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


class InvitationService:
    @staticmethod
    async def send_invitation(
        uow: IUnitOfWork, invitation_data: SendInvitation, sender_id: int
    ) -> InvitationBase:
        async with uow:
            owner = await uow.member.find_owner(
                user_id=sender_id, company_id=invitation_data.company_id
            )

            if not owner:
                logger.error("Only the owner can send invitations")
                raise UnAuthorizedException()

            existing_member = await uow.member.find_one(
                user_id=invitation_data.receiver_id,
                company_id=invitation_data.company_id,
            )

            if existing_member:
                logger.error("User already works in the company")
                raise Exception("User is already a member of the company")

            invitation_dict = invitation_data.model_dump()
            invitation_dict["sender_id"] = sender_id
            invitation_dict["created_at"] = datetime.now()
            invitation_dict["updated_at"] = datetime.now()
            invitation = await uow.invitation.add_one(invitation_dict)
            await uow.commit()

            return InvitationBase(**invitation.__dict__)

    @staticmethod
    async def get_invitations(
        uow: IUnitOfWork, user_id: int, skip: int = 0, limit: int = 10
    ) -> InvitationsListResponse:
        async with uow:
            invitations = await uow.invitation.find_all_by_receiver(
                receiver_id=user_id, skip=skip, limit=limit
            )
            invitation_list = InvitationsListResponse(
                invitations=[
                    InvitationBase(**invitation.__dict__) for invitation in invitations
                ],
                total=len(invitations),
            )

            return invitation_list

    @staticmethod
    async def get_sent_invitations(
        uow: IUnitOfWork, user_id: int, skip: int = 0, limit: int = 10
    ) -> InvitationsListResponse:
        async with uow:

            invitations = await uow.invitation.find_all_by_sender(
                sender_id=user_id, skip=skip, limit=limit
            )
            invitation_list = InvitationsListResponse(
                invitations=[
                    InvitationBase(**invitation.__dict__) for invitation in invitations
                ],
                total=len(invitations),
            )
            return invitation_list

    @staticmethod
    async def cancel_invitation(
        uow: IUnitOfWork, invitation_id: int, sender_id: int
    ) -> int:
        async with uow:
            invitation = await uow.invitation.find_one(id=invitation_id)
            if not invitation:
                logger.error("Invitation not found")
                raise NotFoundException()

            if invitation.sender_id != sender_id:
                logger.error("Only the sender can cancel the invitation")
                raise UnAuthorizedException()

            if invitation.status != "pending":
                logger.error("Invitation has already been accepted or declined")
                raise UnAuthorizedException()

            cancelled_invitation = await uow.invitation.delete_one(invitation_id)
            await uow.commit()
            return cancelled_invitation.id

    @staticmethod
    async def accept_invitation(
        uow: IUnitOfWork, invitation_id: int, receiver_id: int
    ) -> InvitationResponse:
        async with uow:
            invitation = await uow.invitation.find_one(id=invitation_id)
            if not invitation:
                logger.error("Invitation not found")
                raise NotFoundException()

            if invitation.receiver_id != receiver_id:
                logger.error("Unauthorized action")
                raise UnAuthorizedException()

            if invitation.status != "pending":
                logger.error("Invitation has already been accepted or declined")
                raise UnAuthorizedException()

            member_data = MemberCreate(
                user_id=receiver_id, company_id=invitation.company_id, role=2
            )
            await uow.member.add_one(member_data.model_dump(exclude={"id"}))
            await uow.invitation.edit_one(
                invitation_id, {"status": "accepted", "updated_at": datetime.now()}
            )
            await uow.commit()

            company = await uow.company.find_one(id=invitation.company_id)
            user = await uow.user.find_one(id=receiver_id)
            return InvitationResponse(
                title=invitation.title,
                description=invitation.description,
                company_name=company.name,
                receiver_name=user.username,
                status="accepted",
            )

    @staticmethod
    async def decline_invitation(
        uow: IUnitOfWork, invitation_id: int, receiver_id: int
    ) -> InvitationResponse:
        async with uow:
            invitation = await uow.invitation.find_one(id=invitation_id)
            if not invitation:
                logger.error("Invitation not found")
                raise NotFoundException()

            if invitation.receiver_id != receiver_id:
                logger.error("Unauthorized action")
                raise UnAuthorizedException()

            if invitation.status != "pending":
                logger.error("Invitation has already been accepted or declined")
                raise UnAuthorizedException()

            await uow.invitation.edit_one(
                invitation_id, {"status": "declined", "updated_at": datetime.now()}
            )
            await uow.commit()

            company = await uow.company.find_one(id=invitation.company_id)
            user = await uow.user.find_one(id=receiver_id)
            response = InvitationResponse(
                title=invitation.title,
                description=invitation.description,
                company_name=company.name,
                receiver_name=user.username,
                status="declined",
            )
            return response
