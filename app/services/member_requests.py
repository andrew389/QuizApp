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
        """
        async with uow:
            if await MemberRequests._is_existing_member(uow, user_id, company_id):
                raise UnAuthorizedException()
            owner = await uow.company.find_one(id=company_id)
            invitation = await MemberRequests._create_invitation(
                uow, request, user_id, owner.owner_id
            )
            await uow.commit()
            return InvitationBase(**invitation.__dict__)

    @staticmethod
    async def _is_existing_member(
        uow: IUnitOfWork, user_id: int, company_id: int
    ) -> bool:
        """
        Check if the user is already a member of the company.
        """
        existing_member = await uow.member.find_one(
            user_id=user_id, company_id=company_id
        )
        if existing_member:
            logger.error("User is already a member of the company")
            return True
        return False

    @staticmethod
    async def _create_invitation(
        uow: IUnitOfWork, request: MemberRequest, user_id: int, receiver_id: int
    ):
        """
        Create a new invitation with pending status.
        """
        invitation_data = SendInvitation(
            title=request.title,
            description=request.description,
            receiver_id=receiver_id,
            company_id=request.company_id,
        )
        invitation_dict = invitation_data.model_dump()
        invitation_dict.update({"sender_id": user_id, "status": "pending"})
        return await uow.invitation.add_one(invitation_dict)

    @staticmethod
    async def cancel_request_to_join(
        uow: IUnitOfWork, request_id: int, sender_id: int
    ) -> int:
        """
        Cancel a request to join a company.
        """
        async with uow:
            invitation = await uow.invitation.find_one(id=request_id)
            MemberRequests._validate_invitation_for_cancel(invitation, sender_id)
            cancelled_request = await uow.invitation.delete_one(request_id)
            await uow.commit()
            return cancelled_request.id

    @staticmethod
    def _validate_invitation_for_cancel(invitation, sender_id):
        """
        Validate that the invitation can be cancelled.
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
            await uow.commit()
            return await MemberRequests._create_invitation_response(
                uow, request, "accepted"
            )

    @staticmethod
    def _validate_request_for_accept(request):
        """
        Validate that the request can be accepted.
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
        """
        async with uow:
            request = await uow.invitation.find_one(id=request_id)
            MemberRequests._validate_request_for_accept(request)
            await MemberRequests.validate_owner(uow, owner_id, request.company_id)
            await uow.invitation.edit_one(request_id, {"status": "declined"})
            await uow.commit()
            return await MemberRequests._create_invitation_response(
                uow, request, "declined"
            )

    @staticmethod
    async def validate_owner(uow: IUnitOfWork, user_id: int, company_id: int):
        """
        Validate that the user is the owner of the company.
        """
        owner = await uow.member.find_owner(user_id=user_id, company_id=company_id)
        if not owner:
            logger.error("Only the owner can accept requests")
            raise UnAuthorizedException()
