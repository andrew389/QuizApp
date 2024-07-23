from typing import List, Optional

from pydantic import BaseModel


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
    notifications: List[NotificationBase]
    total: int
