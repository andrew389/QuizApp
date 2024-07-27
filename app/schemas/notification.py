from typing import List, Optional

from pydantic import BaseModel

from app.schemas.pagination import PaginationLinks


class NotificationBase(BaseModel):
    id: Optional[int] = None
    message: str
    receiver_id: int
    company_id: int
    status: Optional[str] = "pending"


class NotificationCreate(BaseModel):
    message: str
    receiver_id: int
    company_id: int
    status: Optional[str] = "pending"


class NotificationResponse(BaseModel):
    message: str
    receiver_id: int
    company_id: int
    status: Optional[str] = "pending"


class NotificationsListResponse(BaseModel):
    links: PaginationLinks
    notifications: List[NotificationBase]
    total: int
