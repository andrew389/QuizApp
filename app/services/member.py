from datetime import datetime

from app.core.logger import logger
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException
from app.models.models import Company, Member
from app.schemas.invitation import InvitationBase, SendInvitation, InvitationResponse
from app.schemas.member import (
    MemberCreate,
    MemberUpdate,
    MembersListResponse,
    MemberBase,
)
from app.uow.unitofwork import IUnitOfWork


class MemberService:
    @staticmethod
    async def create_member(uow: IUnitOfWork, member_data: MemberCreate) -> MemberBase:
        async with uow:
            member = await uow.member.add_one(member_data.dict())
            return member

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
    async def update_member(
        uow: IUnitOfWork, member_id: int, member_data: MemberUpdate
    ) -> MemberBase:
        async with uow:
            updated_member = await uow.member.edit_one(
                member_id, member_data.dict(exclude_unset=True)
            )
            return updated_member

    @staticmethod
    async def delete_member(uow: IUnitOfWork, member_id: int) -> int:
        async with uow:
            deleted_member_id = await uow.member.delete_one(member_id)
            return deleted_member_id

    @staticmethod
    async def request_to_join_company(
        uow: IUnitOfWork, user_id: int, company_id: int, title: str, description: str
    ) -> InvitationBase:
        async with uow:
            existing_member = await uow.member.find_one(
                user_id=user_id, company_id=company_id
            )
            logger.info(f"{existing_member}")
            if existing_member:
                logger.error("User is already a member of the company")
                raise UnAuthorizedException()

            owner = await uow.company.find_one(id=company_id)

            invitation_data = SendInvitation(
                title=title,
                description=description,
                receiver_id=owner.owner_id,
                company_id=company_id,
            )
            invitation_dict = invitation_data.model_dump()
            invitation_dict["sender_id"] = user_id
            invitation_dict["created_at"] = datetime.now()
            invitation_dict["updated_at"] = datetime.now()
            invitation_dict["status"] = "pending"

            invitation = await uow.invitation.add_one(invitation_dict)
            await uow.commit()
            return InvitationBase(**invitation.__dict__)

    @staticmethod
    async def cancel_request_to_join(
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
    async def accept_request(
        uow: IUnitOfWork, owner_id: int, request_id: int
    ) -> InvitationResponse:
        async with uow:
            request = await uow.invitation.find_one(id=request_id)
            if not request:
                logger.error("Request not found")
                raise NotFoundException()

            if request.status != "pending":
                logger.error("Invitation has already been accepted or declined")
                raise UnAuthorizedException()

            owner = await uow.member.find_owner(
                user_id=owner_id, company_id=request.company_id
            )
            if not owner:
                logger.error("Only the owner can accept requests")
                raise UnAuthorizedException()

            await uow.invitation.edit_one(
                request_id, {"status": "accepted", "updated_at": datetime.now()}
            )

            member_data = MemberCreate(
                user_id=request.sender_id, company_id=request.company_id, role=2
            )
            await uow.member.add_one(member_data.model_dump(exclude={"id"}))
            await uow.commit()

            company = await uow.company.find_one(id=request.company_id)
            user = await uow.user.find_one(id=request.receiver_id)
            return InvitationResponse(
                title=request.title,
                description=request.description,
                company_name=company.name,
                receiver_name=user.username,
                status="accepted",
            )

    @staticmethod
    async def decline_request(
        uow: IUnitOfWork, owner_id: int, request_id: int
    ) -> InvitationResponse:
        async with uow:
            request = await uow.invitation.find_one(id=request_id)
            if not request:
                logger.error("Request not found")
                raise NotFoundException()

            if request.status != "pending":
                logger.error("Invitation has already been accepted or declined")
                raise UnAuthorizedException()

            owner = await uow.member.find_owner(
                user_id=owner_id, company_id=request.company_id
            )
            if not owner:
                logger.error("Only the owner can decline requests")
                raise UnAuthorizedException()

            await uow.invitation.edit_one(
                request_id, {"status": "declined", "updated_at": datetime.now()}
            )
            await uow.commit()
            company = await uow.company.find_one(id=request.company_id)
            user = await uow.user.find_one(id=request.receiver_id)
            return InvitationResponse(
                title=request.title,
                description=request.description,
                company_name=company.name,
                receiver_name=user.username,
                status="declined",
            )

    @staticmethod
    async def remove_member(
        uow: IUnitOfWork, user_id: int, member_id: int
    ) -> MemberBase:
        async with uow:
            member = await uow.member.find_one(id=member_id)
            if not member:
                logger.error("Member not found")
                raise NotFoundException()

            owner = await uow.member.find_owner(
                user_id=user_id, company_id=member.company_id
            )
            if not owner or owner.role != 1:
                logger.error("Only the owner can remove members")
                raise UnAuthorizedException()

            if owner.id == member_id:
                logger.error("You can't remove owner")
                raise UnAuthorizedException()

            if user_id == member_id:
                logger.error("You can't remove yourself")
                raise UnAuthorizedException()

            updated_member = await uow.member.edit_one(
                member_id, {"role": 0, "company_id": None}
            )
            await uow.commit()
            return updated_member

    @staticmethod
    async def leave_company(
        uow: IUnitOfWork, user_id: int, company_id: int
    ) -> MemberBase:
        async with uow:
            member = await uow.member.find_one(user_id=user_id, company_id=company_id)

            if not member or member.role == 1:
                logger.error("Leaving exception")
                raise UnAuthorizedException()

            updated_member = await uow.member.edit_one(
                member.id, {"role": 0, "company_id": None}
            )
            await uow.commit()
            return updated_member
