from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.db.pg_db import Base


class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): The unique identifier for the user.
        password (str): The hashed password of the user.
        email (str): The email address of the user. This must be unique.
        is_active (bool): Indicates whether the user is active. Defaults to True.
        firstname (str): The first name of the user.
        lastname (str): The last name of the user.
        city (str): The city where the user resides.
        phone (str): The phone number of the user.
        avatar (str): The URL or path to the user's avatar image.
        is_superuser (bool): Indicates whether the user has superuser privileges. Defaults to False.
        created_at (datetime): The timestamp when the user record was created. Defaults to the current time.
        updated_at (datetime): The timestamp when the user record was last updated. Updates automatically on modification.

    Relationships:
        companies (relationship): The list of companies associated with the user.
        memberships (relationship): The list of memberships the user holds.
        sent_invitations (relationship): The list of invitations sent by the user.
        received_invitations (relationship): The list of invitations received by the user.
        received_notifications (relationship): The list of notifications received by the user.
        answered_questions (relationship): The list of questions answered by the user.
    """

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
    received_notifications = relationship(
        "Notification",
        foreign_keys="Notification.receiver_id",
        back_populates="receiver",
    )
    answered_questions = relationship("AnsweredQuestion", back_populates="user")
