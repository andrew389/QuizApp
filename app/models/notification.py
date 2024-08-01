from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.pg_db import Base


class Notification(Base):
    """
    Represents a notification sent to a user within a company.

    Attributes:
        id (int): The unique identifier for the notification.
        message (str): The content of the notification message. This field is required.
        receiver_id (int): The identifier of the user who receives the notification. This field is required.
        company_id (int): The identifier of the company associated with the notification. This field is required.
        status (str): The current status of the notification (e.g., "pending"). Defaults to "pending".
        created_at (datetime): The timestamp when the notification was created. Defaults to the current time.

    Relationships:
        receiver (relationship): The user who receives the notification.
        company (relationship): The company associated with the notification.
    """

    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    receiver_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    company_id = Column(
        Integer, ForeignKey("company.id", ondelete="CASCADE"), nullable=False
    )
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)

    receiver = relationship(
        "User", foreign_keys=[receiver_id], back_populates="received_notifications"
    )
    company = relationship("Company", back_populates="notifications")
