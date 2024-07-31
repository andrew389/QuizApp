from typing import List, Optional
from pydantic import BaseModel
from app.schemas.pagination import PaginationLinks


class InvitationBase(BaseModel):
    """
    Base schema for an invitation.

    Attributes:
        id (Optional[int]): The unique identifier of the invitation. Default is None.
        title (str): The title of the invitation.
        description (str): A brief description of the invitation.
        sender_id (int): The ID of the user sending the invitation.
        receiver_id (int): The ID of the user receiving the invitation.
        company_id (int): The ID of the associated company.
        status (Optional[str]): The status of the invitation, default is "pending".
    """

    id: Optional[int] = None
    title: str
    description: str
    sender_id: int
    receiver_id: int
    company_id: int
    status: Optional[str] = "pending"


class SendInvitation(BaseModel):
    """
    Schema for sending an invitation.

    Attributes:
        title (str): The title of the invitation.
        description (str): A brief description of the invitation.
        receiver_id (int): The ID of the user receiving the invitation.
    """

    title: str
    description: str
    receiver_id: int


class InvitationResponse(BaseModel):
    """
    Schema for the response after sending an invitation.

    Attributes:
        title (str): The title of the invitation.
        description (str): A brief description of the invitation.
        company_name (str): The name of the associated company.
        receiver_email (str): The email of the user receiving the invitation.
        status (Optional[str]): The status of the invitation, default is "pending".
    """

    title: str
    description: str
    company_name: str
    receiver_email: str
    status: Optional[str] = "pending"


class InvitationsListResponse(BaseModel):
    """
    Schema for a paginated response containing a list of invitations.

    Attributes:
        links (PaginationLinks): Pagination links for navigating through the list.
        invitations (List[InvitationBase]): A list of invitations.
        total (int): The total number of invitations.
    """

    links: PaginationLinks
    invitations: List[InvitationBase]
    total: int
