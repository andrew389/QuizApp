from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.pagination import PaginationLinks


class NotificationBase(BaseModel):
    """
    Base schema for a notification.
    """

    id: Optional[int] = Field(
        None, description="The unique identifier of the notification. Default is None."
    )
    message: str = Field(..., description="The content of the notification message.")
    receiver_id: int = Field(
        ..., description="The ID of the receiver of the notification."
    )
    company_id: int = Field(..., description="The ID of the associated company.")
    status: Optional[str] = Field(
        "pending", description='The status of the notification, default is "pending".'
    )


class NotificationCreate(BaseModel):
    """
    Schema for creating a notification.
    """

    message: str = Field(..., description="The content of the notification message.")
    receiver_id: int = Field(
        ..., description="The ID of the receiver of the notification."
    )
    company_id: int = Field(..., description="The ID of the associated company.")
    status: Optional[str] = Field(
        "pending", description='The status of the notification, default is "pending".'
    )


class NotificationResponse(BaseModel):
    """
    Schema for a notification response.
    """

    message: str = Field(..., description="The content of the notification message.")
    receiver_id: int = Field(
        ..., description="The ID of the receiver of the notification."
    )
    company_id: int = Field(..., description="The ID of the associated company.")
    status: Optional[str] = Field(
        "pending", description='The status of the notification, default is "pending".'
    )


class NotificationsListResponse(BaseModel):
    """
    Schema for a paginated response containing a list of notifications.
    """

    links: PaginationLinks = Field(
        ..., description="Pagination links for navigating through the list."
    )
    notifications: List[NotificationBase] = Field(
        ..., description="A list of notifications."
    )
    total: int = Field(..., description="The total number of notifications.")
