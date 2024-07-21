from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.db.pg_db import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    firstname = Column(String)
    lastname = Column(String)
    city = Column(String)
    phone = Column(String)
    avatar = Column(String)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    companies = relationship("Company", back_populates="user")
    memberships = relationship("Member", back_populates="user")
    sent_invitations = relationship(
        "Invitation", foreign_keys="Invitation.sender_id", back_populates="sender"
    )
    received_invitations = relationship(
        "Invitation", foreign_keys="Invitation.receiver_id", back_populates="receiver"
    )
