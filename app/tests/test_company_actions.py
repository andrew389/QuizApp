import pytest
from fastapi import Request
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.exceptions.auth import UnAuthorizedException
from app.schemas.invitation import SendInvitation
from app.services.invitation import InvitationService
from app.services.member_requests import MemberRequests
from app.services.member_queries import MemberQueries
from app.services.member_management import MemberManagement
from app.schemas.member import MembersListResponse, MemberBase, AdminsListResponse
from app.uow.unitofwork import IUnitOfWork
from app.utils.role import Role


@pytest.mark.asyncio
async def test_get_members():
    mock_uow = AsyncMock(spec=IUnitOfWork)
    setattr(mock_uow, "member", AsyncMock())

    request = MagicMock(Request)

    mock_uow.member.find_all_by_company.return_value = [
        MemberBase(
            id=1,
            user_id=1,
            company_id=1,
            role=Role.MEMBER.value,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
    ]
    with pytest.raises(TypeError):
        await MemberQueries.get_members(
            mock_uow, company_id=1, request=request, skip=0, limit=10
        )


@pytest.mark.asyncio
async def test_get_member_by_id():
    mock_uow = AsyncMock(spec=IUnitOfWork)
    setattr(mock_uow, "member", AsyncMock())
    mock_uow.member.find_one.return_value = MemberBase(
        id=1,
        user_id=1,
        company_id=1,
        role=Role.MEMBER.value,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    response = await MemberQueries.get_member_by_id(mock_uow, member_id=1, company_id=1)

    assert isinstance(response, MemberBase)
    assert response.id == 1


@pytest.mark.asyncio
async def test_cancel_request_to_join():
    mock_uow = AsyncMock(spec=IUnitOfWork)
    setattr(mock_uow, "invitation", AsyncMock())
    mock_uow.invitation.find_one.return_value = AsyncMock(sender_id=1, status="pending")

    request_id = 1

    response = await MemberRequests.cancel_request_to_join(
        mock_uow, request_id=request_id, sender_id=1
    )

    assert isinstance(response, int) == False


@pytest.mark.asyncio
async def test_remove_member():
    mock_uow = AsyncMock(spec=IUnitOfWork)
    setattr(mock_uow, "member", AsyncMock())
    mock_uow.member.find_one.return_value = AsyncMock(
        id=2, user_id=2, company_id=1, role=Role.MEMBER.value
    )

    user_id = 1
    member_id = 1

    with pytest.raises(UnAuthorizedException):
        await MemberManagement.remove_member(
            mock_uow, user_id=user_id, member_id=member_id
        )


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
async def test_appoint_admin():
    mock_uow = AsyncMock(spec=IUnitOfWork)
    setattr(mock_uow, "member", AsyncMock())

    owner_id = 1
    member_id = 2
    company_id = 1
    member_data = AsyncMock(id=2, user_id=2, company_id=1, role=Role.MEMBER.value)
    updated_member_data = AsyncMock(
        id=2, user_id=2, company_id=1, role=Role.ADMIN.value
    )

    mock_uow.member.find_one.return_value = member_data
    mock_uow.member.edit_one.return_value = updated_member_data

    response = await MemberManagement.appoint_admin(
        mock_uow, owner_id, company_id=company_id, member_id=member_id
    )

    assert isinstance(response, MemberBase)
    assert response.role == Role.ADMIN.value


@pytest.mark.asyncio
async def test_get_admins():
    mock_uow = AsyncMock(spec=IUnitOfWork)
    setattr(mock_uow, "member", AsyncMock())

    request = MagicMock(Request)

    company_id = 1
    admins_data = [
        AsyncMock(id=1, user_id=1, company_id=1, role=Role.ADMIN.value),
        AsyncMock(id=2, user_id=2, company_id=1, role=Role.ADMIN.value),
    ]

    mock_uow.member.find_all_by_company_and_role.return_value = admins_data

    with pytest.raises(TypeError):
        await MemberQueries.get_admins(
            mock_uow, company_id=company_id, request=request, skip=0, limit=10
        )
