from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.pagination import PaginationLinks


class InvitationBase(BaseModel):
    """
    Base schema for an invitation.
    """

    id: Optional[int] = Field(
        None, description="The unique identifier of the invitation. Default is None."
    )
    title: str = Field(..., description="The title of the invitation.")
    description: str = Field(..., description="A brief description of the invitation.")
    sender_id: int = Field(
        ..., description="The ID of the user sending the invitation."
    )
    receiver_id: int = Field(
        ..., description="The ID of the user receiving the invitation."
    )
    company_id: int = Field(..., description="The ID of the associated company.")
    status: Optional[str] = Field(
        "pending", description="The status of the invitation, default is 'pending'."
    )


class SendInvitation(BaseModel):
    """
    Schema for sending an invitation.
    """

    title: str = Field(..., description="The title of the invitation.")
    description: str = Field(..., description="A brief description of the invitation.")
    receiver_id: int = Field(
        ..., description="The ID of the user receiving the invitation."
    )


class InvitationResponse(BaseModel):
    """
    Schema for the response after sending an invitation.
    """

    title: str = Field(..., description="The title of the invitation.")
    description: str = Field(..., description="A brief description of the invitation.")
    company_name: str = Field(..., description="The name of the associated company.")
    receiver_email: str = Field(
        ..., description="The email of the user receiving the invitation."
    )
    status: Optional[str] = Field(
        "pending", description="The status of the invitation, default is 'pending'."
    )


class InvitationsListResponse(BaseModel):
    """
    Schema for a paginated response containing a list of invitations.
    """

    links: PaginationLinks = Field(
        ..., description="Pagination links for navigating through the list."
    )
    invitations: List[InvitationBase] = Field(..., description="A list of invitations.")
    total: int = Field(..., description="The total number of invitations.")
