from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.pagination import PaginationLinks


class MemberBase(BaseModel):
    """
    Base schema for a member.
    """

    id: Optional[int] = Field(
        None, description="The unique identifier of the member. Default is None."
    )
    user_id: int = Field(..., description="The ID of the user who is a member.")
    company_id: Optional[int] = Field(
        None, description="The ID of the associated company. Default is None."
    )
    role: int = Field(..., description="The role of the member within the company.")


class MemberCreate(MemberBase):
    """
    Schema for creating a member. Inherits from MemberBase.
    """

    pass


class MemberUpdate(BaseModel):
    """
    Schema for updating a member.
    """

    company_id: Optional[int] = Field(
        None, description="The ID of the associated company. Default is None."
    )
    role: int = Field(..., description="The role of the member within the company.")


class MemberDelete(BaseModel):
    """
    Schema for deleting a member.
    """

    id: int = Field(
        ..., description="The unique identifier of the member to be deleted."
    )


class MemberRequest(BaseModel):
    """
    Schema for a member request.
    """

    title: str = Field(..., description="The title of the request.")
    description: str = Field(..., description="A brief description of the request.")


class MembersListResponse(BaseModel):
    """
    Schema for a paginated response containing a list of members.
    """

    links: PaginationLinks = Field(
        ..., description="Pagination links for navigating through the list."
    )
    members: List[MemberBase] = Field(..., description="A list of members.")
    total: int = Field(..., description="The total number of members.")


class AdminsListResponse(BaseModel):
    """
    Schema for a paginated response containing a list of admins.
    """

    links: PaginationLinks = Field(
        ..., description="Pagination links for navigating through the list."
    )
    admins: List[MemberBase] = Field(..., description="A list of admins.")
    total: int = Field(..., description="The total number of admins.")
