from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.pg_db import Base


class Invitation(Base):
    """
    Represents an invitation sent from one user to another within a company.

    Attributes:
        id (int): The unique identifier for the invitation.
        title (str): The title of the invitation. This field is required.
        description (str): A description of the invitation. This field is required.
        sender_id (int): The identifier of the user who sent the invitation. This field is required.
        receiver_id (int): The identifier of the user who is the recipient of the invitation. This field is required.
        company_id (int): The identifier of the company associated with the invitation. This field is required.
        created_at (datetime): The timestamp when the invitation was created. Defaults to the current time.
        updated_at (datetime): The timestamp when the invitation was last updated. Updates automatically on modification.
        status (str): The current status of the invitation (e.g., "pending"). Defaults to "pending".

    Relationships:
        sender (relationship): The user who sent the invitation.
        receiver (relationship): The user who received the invitation.
        company (relationship): The company associated with the invitation.
    """

    __tablename__ = "invitation"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    sender_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    company_id = Column(
        Integer, ForeignKey("company.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )
    status = Column(String, default="pending")

    sender = relationship(
        "User", foreign_keys=[sender_id], back_populates="sent_invitations"
    )
    receiver = relationship(
        "User", foreign_keys=[receiver_id], back_populates="received_invitations"
    )
    company = relationship("Company", back_populates="invitations")
