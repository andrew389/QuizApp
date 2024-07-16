import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from app.exceptions.auth import UnAuthorizedException
from app.schemas.invitation import InvitationBase, SendInvitation, InvitationResponse
from app.services.invitation import InvitationService
from app.services.member import MemberService
from app.schemas.member import MembersListResponse, MemberBase
from app.uow.unitofwork import IUnitOfWork


@pytest.mark.asyncio
async def test_get_members():
    mock_uow = AsyncMock(spec=IUnitOfWork)
    setattr(mock_uow, "member", AsyncMock())
    mock_uow.member.find_all_by_company.return_value = [
        MemberBase(
            id=1,
            user_id=1,
            company_id=1,
            role=2,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
    ]

    response = await MemberService.get_members(mock_uow, company_id=1, skip=0, limit=10)

    assert isinstance(response, MembersListResponse)
    assert len(response.members) == 1
    assert response.total == 1


@pytest.mark.asyncio
async def test_get_member_by_id():
    mock_uow = AsyncMock(spec=IUnitOfWork)
    setattr(mock_uow, "member", AsyncMock())
    mock_uow.member.find_one.return_value = MemberBase(
        id=1,
        user_id=1,
        company_id=1,
        role=2,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    response = await MemberService.get_member_by_id(mock_uow, member_id=1)

    assert isinstance(response, MemberBase)
    assert response.id == 1


@pytest.mark.asyncio
async def test_cancel_request_to_join():
    mock_uow = AsyncMock(spec=IUnitOfWork)
    setattr(mock_uow, "invitation", AsyncMock())
    mock_uow.invitation.find_one.return_value = AsyncMock(sender_id=1, status="pending")

    invitation_id = 1

    response = await MemberService.cancel_request_to_join(
        mock_uow, invitation_id=invitation_id, sender_id=1
    )

    assert isinstance(response, int) == False


@pytest.mark.asyncio
async def test_remove_member():
    mock_uow = AsyncMock(spec=IUnitOfWork)
    setattr(mock_uow, "member", AsyncMock())
    mock_uow.member.find_one.return_value = AsyncMock(
        id=2, user_id=2, company_id=1, role=2
    )

    user_id = 1
    member_id = 2

    with pytest.raises(UnAuthorizedException):
        await MemberService.remove_member(
            mock_uow, user_id=user_id, member_id=member_id
        )


@pytest.mark.asyncio
async def test_leave_company():
    mock_uow = AsyncMock(spec=IUnitOfWork)
    setattr(mock_uow, "member", AsyncMock())
    mock_uow.member.find_one.return_value = AsyncMock(
        id=1, user_id=1, company_id=1, role=2
    )

    user_id = 1
    company_id = 1

    response = await MemberService.leave_company(
        mock_uow, user_id=user_id, company_id=company_id
    )

    assert isinstance(response, MemberBase) == False


@pytest.mark.asyncio
async def test_send_invitation():
    mock_uow = AsyncMock(spec=IUnitOfWork)
    setattr(mock_uow, "member", AsyncMock())
    mock_uow.member.find_owner.return_value = AsyncMock(user_id=1)

    invitation_data = SendInvitation(
        title="dede", description="ddede", sender_id=1, receiver_id=3, company_id=1
    )

    with pytest.raises(Exception):
        await InvitationService.send_invitation(
            mock_uow, sender_id=1, invitation_data=invitation_data
        )


@pytest.mark.asyncio
async def test_cancel_invitation():
    mock_uow = AsyncMock(spec=IUnitOfWork)
    setattr(mock_uow, "invitation", AsyncMock())
    mock_uow.invitation.find_one.return_value = AsyncMock(sender_id=1, status="pending")

    response = await InvitationService.cancel_invitation(
        mock_uow, invitation_id=1, sender_id=1
    )

    assert isinstance(response, SendInvitation) == False
