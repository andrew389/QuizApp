from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.pg_db import Base


class Quiz(Base):
    """
    Represents a quiz within a company.

    Attributes:
        id (int): The unique identifier for the quiz.
        title (str): The title of the quiz. This field is required.
        description (str): A description of the quiz. This field is optional.
        frequency (int): The frequency of the quiz, representing how often it should be presented. Defaults to 0.
        company_id (int): The identifier of the company that owns the quiz. This field is required.
        created_at (datetime): The timestamp when the quiz was created. Defaults to the current time.
        updated_at (datetime): The timestamp when the quiz was last updated. Updates automatically on modification.

    Relationships:
        company (relationship): The company that owns the quiz.
        questions (relationship): The list of questions associated with the quiz.
        answered_questions (relationship): The list of answered questions related to the quiz.
    """

    __tablename__ = "quiz"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    frequency = Column(Integer, default=0)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    company = relationship("Company", back_populates="quizzes")
    questions = relationship(
        "Question", back_populates="quiz", cascade="all, delete-orphan"
    )
    answered_questions = relationship("AnsweredQuestion", back_populates="quiz")
