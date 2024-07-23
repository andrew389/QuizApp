from pydantic import BaseModel
from typing import Optional, List


class MemberBase(BaseModel):
    id: Optional[int] = None
    user_id: int
    company_id: Optional[int] = None
    role: int


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    company_id: Optional[int] = None
    role: int


class MemberDelete(BaseModel):
    id: int


class MemberRequest(BaseModel):
    title: str
    description: str


class MembersListResponse(BaseModel):
    members: List[MemberBase]
    total: int


class AdminsListResponse(BaseModel):
    admins: List[MemberBase]
    total: int
