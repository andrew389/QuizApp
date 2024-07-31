from typing import List, Optional
from pydantic import BaseModel
from app.schemas.pagination import PaginationLinks


class MemberBase(BaseModel):
    """
    Base schema for a member.

    Attributes:
        id (Optional[int]): The unique identifier of the member. Default is None.
        user_id (int): The ID of the user who is a member.
        company_id (Optional[int]): The ID of the associated company. Default is None.
        role (int): The role of the member within the company.
    """

    id: Optional[int] = None
    user_id: int
    company_id: Optional[int] = None
    role: int


class MemberCreate(MemberBase):
    """
    Schema for creating a member. Inherits from MemberBase.
    """

    pass


class MemberUpdate(BaseModel):
    """
    Schema for updating a member.

    Attributes:
        company_id (Optional[int]): The ID of the associated company. Default is None.
        role (int): The role of the member within the company.
    """

    company_id: Optional[int] = None
    role: int


class MemberDelete(BaseModel):
    """
    Schema for deleting a member.

    Attributes:
        id (int): The unique identifier of the member to be deleted.
    """

    id: int


class MemberRequest(BaseModel):
    """
    Schema for a member request.

    Attributes:
        title (str): The title of the request.
        description (str): A brief description of the request.
    """

    title: str
    description: str


class MembersListResponse(BaseModel):
    """
    Schema for a paginated response containing a list of members.

    Attributes:
        links (PaginationLinks): Pagination links for navigating through the list.
        members (List[MemberBase]): A list of members.
        total (int): The total number of members.
    """

    links: PaginationLinks
    members: List[MemberBase]
    total: int


class AdminsListResponse(BaseModel):
    """
    Schema for a paginated response containing a list of admins.

    Attributes:
        links (PaginationLinks): Pagination links for navigating through the list.
        admins (List[MemberBase]): A list of admins.
        total (int): The total number of admins.
    """

    links: PaginationLinks
    admins: List[MemberBase]
    total: int
