from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.pg_db import Base


class Member(Base):
    """
    Represents a membership of a user within a company.

    Attributes:
        id (int): The unique identifier for the membership.
        user_id (int): The identifier of the user who holds the membership. This field is required.
        company_id (int): The identifier of the company where the user is a member. This field is optional.
        role (int): The role of the user within the company (e.g., admin, member). This field is required.
        created_at (datetime): The timestamp when the membership record was created. Defaults to the current time.
        updated_at (datetime): The timestamp when the membership record was last updated. Updates automatically on modification.

    Relationships:
        user (relationship): The user who holds the membership.
        company (relationship): The company associated with the membership.
    """

    __tablename__ = "member"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    company_id = Column(
        Integer, ForeignKey("company.id", ondelete="CASCADE"), nullable=True
    )
    role = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    user = relationship("User", back_populates="memberships")
    company = relationship("Company", back_populates="members")
