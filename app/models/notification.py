from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.pg_db import Base


class Notification(Base):
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
