from typing import List, Optional

from pydantic import BaseModel

from app.schemas.pagination import PaginationLinks


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
    links: PaginationLinks
    members: List[MemberBase]
    total: int


class AdminsListResponse(BaseModel):
    links: PaginationLinks
    admins: List[MemberBase]
    total: int
