from typing import List, Optional

from pydantic import BaseModel


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
    company_id: int
    title: str
    description: str


class AdminRequest(BaseModel):
    company_id: int
    member_id: int


class MembersListResponse(BaseModel):
    members: List[MemberBase]
    total: int
