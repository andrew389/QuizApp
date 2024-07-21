from app.core.logger import logger
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException
from app.schemas.invitation import InvitationBase, SendInvitation, InvitationResponse
from app.schemas.member import (
    MemberCreate,
    MembersListResponse,
    MemberBase,
    MemberRequest,
)
from app.uow.unitofwork import IUnitOfWork
from app.utils.role import Role


class MemberService:

    @staticmethod
    async def get_members(
        uow: IUnitOfWork, company_id: int, skip: int = 0, limit: int = 10
    ) -> MembersListResponse:
        async with uow:
            members = await uow.member.find_all_by_company(
                company_id=company_id, skip=skip, limit=limit
            )
            member_list = MembersListResponse(
                members=[MemberBase(**member.__dict__) for member in members],
                total=len(members),
            )
            return member_list

    @staticmethod
    async def get_member_by_id(uow: IUnitOfWork, member_id: int) -> MemberBase:
        async with uow:
            member = await uow.member.find_one(id=member_id)
            return member

    @staticmethod
    async def request_to_join_company(
        uow: IUnitOfWork, user_id: int, request: MemberRequest, company_id: int
    ) -> InvitationBase:
        async with uow:
            if await MemberService._is_existing_member(uow, user_id, company_id):
                raise UnAuthorizedException()

            owner = await uow.company.find_one(id=company_id)
            invitation = await MemberService._create_invitation(
                uow, request, user_id, owner.owner_id
            )
            await uow.commit()
            return InvitationBase(**invitation.__dict__)

    @staticmethod
    async def _is_existing_member(
        uow: IUnitOfWork, user_id: int, company_id: int
    ) -> bool:
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
        invitation_data = SendInvitation(
            title=request.title,
            description=request.description,
            receiver_id=receiver_id,
            company_id=request.company_id,
        )
        invitation_dict = invitation_data.model_dump()
        invitation_dict["sender_id"] = user_id
        invitation_dict["status"] = "pending"
        invitation = await uow.invitation.add_one(invitation_dict)
        return invitation

    @staticmethod
    async def cancel_request_to_join(
        uow: IUnitOfWork, request_id: int, sender_id: int
    ) -> int:
        async with uow:
            invitation = await uow.invitation.find_one(id=request_id)
            MemberService._validate_invitation_for_cancel(invitation, sender_id)
            cancelled_request = await uow.invitation.delete_one(request_id)
            await uow.commit()
            return cancelled_request.id

    @staticmethod
    def _validate_invitation_for_cancel(invitation, sender_id):
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
        async with uow:
            request = await uow.invitation.find_one(id=request_id)
            MemberService._validate_request_for_accept(request)
            await MemberService._validate_owner(uow, owner_id, request.company_id)
            await uow.invitation.edit_one(request_id, {"status": "accepted"})
            await MemberService._add_member(uow, request.sender_id, request.company_id)
            await uow.commit()
            return await MemberService._create_invitation_response(
                uow, request, "accepted"
            )

    @staticmethod
    def _validate_request_for_accept(request):
        if not request:
            logger.error("Request not found")
            raise NotFoundException()

        if request.status != "pending":
            logger.error("Invitation has already been accepted or declined")
            raise UnAuthorizedException()

    @staticmethod
    async def _validate_owner(uow: IUnitOfWork, user_id: int, company_id: int):
        owner = await uow.member.find_owner(user_id=user_id, company_id=company_id)
        if not owner:
            logger.error("Only the owner can accept requests")
            raise UnAuthorizedException()

    @staticmethod
    async def _add_member(uow: IUnitOfWork, user_id: int, company_id: int):
        member_data = MemberCreate(
            user_id=user_id, company_id=company_id, role=Role.MEMBER.value
        )
        await uow.member.add_one(member_data.model_dump(exclude={"id"}))

    @staticmethod
    async def _create_invitation_response(
        uow: IUnitOfWork, request, status: str
    ) -> InvitationResponse:
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
        async with uow:
            request = await uow.invitation.find_one(id=request_id)
            MemberService._validate_request_for_accept(request)
            await MemberService._validate_owner(uow, owner_id, request.company_id)
            await uow.invitation.edit_one(request_id, {"status": "declined"})
            await uow.commit()
            return await MemberService._create_invitation_response(
                uow, request, "declined"
            )

    @staticmethod
    async def remove_member(
        uow: IUnitOfWork, user_id: int, member_id: int
    ) -> MemberBase:
        async with uow:
            member = await uow.member.find_one(id=member_id)
            await MemberService._validate_member_for_remove(
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
        owner_or_admin = await uow.member.find_one(id=user_id)

        if owner_or_admin.role not in [Role.OWNER.value, Role.ADMIN.value]:
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
        async with uow:
            member = await uow.member.find_one(user_id=user_id, company_id=company_id)
            MemberService._validate_member_for_leave(member)
            updated_member = await uow.member.edit_one(
                member.id, {"role": Role.UNEMPLOYED.value, "company_id": None}
            )
            await uow.commit()
            return updated_member

    @staticmethod
    def _validate_member_for_leave(member):
        if not member or member.role == Role.OWNER.value:
            logger.error("Leaving exception")
            raise UnAuthorizedException()

    @staticmethod
    async def appoint_admin(
        uow: IUnitOfWork, owner_id: int, company_id: int, member_id: int
    ) -> MemberBase:
        async with uow:
            await MemberService._validate_owner(uow, owner_id, company_id)
            member = await uow.member.find_one(id=member_id)
            if not member or member.role != Role.MEMBER.value:
                logger.error("Member not found or not eligible")
                raise NotFoundException()

            updated_member = await uow.member.edit_one(
                member_id, {"role": Role.ADMIN.value}
            )
            await uow.commit()
            return MemberBase(**updated_member.__dict__)

    @staticmethod
    async def get_admins(
        uow: IUnitOfWork, company_id: int, skip: int = 0, limit: int = 10
    ) -> MembersListResponse:
        async with uow:
            admins = await uow.member.find_all_by_company_and_role(
                company_id=company_id, role=Role.ADMIN.value, skip=skip, limit=limit
            )
            admins_list = MembersListResponse(
                members=[MemberBase(**admin.__dict__) for admin in admins],
                total=len(admins),
            )
            return admins_list
