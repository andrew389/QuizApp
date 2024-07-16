from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class InvitationBase(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    sender_id: int
    receiver_id: int
    company_id: int
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
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
    receiver_name: str
    status: Optional[str] = "pending"


class InvitationsListResponse(BaseModel):
    invitations: List[InvitationBase]
    total: int
