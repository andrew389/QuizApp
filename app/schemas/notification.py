from typing import List, Optional
from pydantic import BaseModel
from app.schemas.pagination import PaginationLinks


class NotificationBase(BaseModel):
    """
    Base schema for a notification.

    Attributes:
        id (Optional[int]): The unique identifier of the notification. Default is None.
        message (str): The content of the notification message.
        receiver_id (int): The ID of the receiver of the notification.
        company_id (int): The ID of the associated company.
        status (Optional[str]): The status of the notification, default is "pending".
    """

    id: Optional[int] = None
    message: str
    receiver_id: int
    company_id: int
    status: Optional[str] = "pending"


class NotificationCreate(BaseModel):
    """
    Schema for creating a notification.

    Attributes:
        message (str): The content of the notification message.
        receiver_id (int): The ID of the receiver of the notification.
        company_id (int): The ID of the associated company.
        status (Optional[str]): The status of the notification, default is "pending".
    """

    message: str
    receiver_id: int
    company_id: int
    status: Optional[str] = "pending"


class NotificationResponse(BaseModel):
    """
    Schema for a notification response.

    Attributes:
        message (str): The content of the notification message.
        receiver_id (int): The ID of the receiver of the notification.
        company_id (int): The ID of the associated company.
        status (Optional[str]): The status of the notification, default is "pending".
    """

    message: str
    receiver_id: int
    company_id: int
    status: Optional[str] = "pending"


class NotificationsListResponse(BaseModel):
    """
    Schema for a paginated response containing a list of notifications.

    Attributes:
        links (PaginationLinks): Pagination links for navigating through the list.
        notifications (List[NotificationBase]): A list of notifications.
        total (int): The total number of notifications.
    """

    links: PaginationLinks
    notifications: List[NotificationBase]
    total: int
