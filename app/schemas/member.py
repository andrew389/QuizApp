from datetime import datetime

from pydantic import BaseModel
from typing import Optional, List


class MemberBase(BaseModel):
    id: Optional[int] = None
    user_id: int
    company_id: Optional[int] = None
    role: int
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    company_id: Optional[int] = None
    role: int
    updated_at: datetime = datetime.now()


class MemberDelete(BaseModel):
    id: int


class MembersListResponse(BaseModel):
    members: List[MemberBase]
    total: int
