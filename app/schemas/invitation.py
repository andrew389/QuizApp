from typing import Optional, List

from pydantic import BaseModel


class InvitationBase(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    sender_id: int
    receiver_id: int
    company_id: int
    status: Optional[str] = "pending"


class SendInvitation(BaseModel):
    title: str
    description: str
    sender_id: Optional[int] = None
    receiver_id: int
    company_id: int


class InvitationResponse(BaseModel):
    title: str
    description: str
    company_name: str
    receiver_email: str
    status: Optional[str] = "pending"


class InvitationsListResponse(BaseModel):
    invitations: List[InvitationBase]
    total: int
