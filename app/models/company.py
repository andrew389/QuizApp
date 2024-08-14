from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.pg_db import Base


class Company(Base):
    """
    Represents a company in the system.

    Attributes:
        id (int): The unique identifier for the company.
        name (str): The name of the company. This field is required.
        description (str): A description of the company. This field is optional.
        owner_id (int): The identifier of the user who owns the company. This field is required.
        is_visible (bool): Indicates whether the company is visible. Defaults to True.
        created_at (datetime): The timestamp when the company record was created. Defaults to the current time.
        updated_at (datetime): The timestamp when the company record was last updated. Updates automatically on modification.

    Relationships:
        user (relationship): The user who owns the company.
        members (relationship): The list of members associated with the company.
        invitations (relationship): The list of invitations related to the company.
        notifications (relationship): The list of notifications related to the company.
        quizzes (relationship): The list of quizzes associated with the company.
        questions (relationship): The list of questions related to the company.
        answers (relationship): The list of answers associated with the company.
        answered_questions (relationship): The list of answered questions related to the company.
    """

    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    is_visible = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    user = relationship("User", back_populates="companies")
    members = relationship(
        "Member", back_populates="company", cascade="all, delete-orphan"
    )
    invitations = relationship(
        "Invitation", back_populates="company", cascade="all, delete-orphan"
    )
    notifications = relationship(
        "Notification", back_populates="company", cascade="all, delete-orphan"
    )
    quizzes = relationship(
        "Quiz", back_populates="company", cascade="all, delete-orphan"
    )
    questions = relationship(
        "Question", back_populates="company", cascade="all, delete-orphan"
    )
    answers = relationship(
        "Answer", back_populates="company", cascade="all, delete-orphan"
    )
    answered_questions = relationship("AnsweredQuestion", back_populates="company")
