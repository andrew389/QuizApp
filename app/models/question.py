from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.pg_db import Base


class Question(Base):
    """
    Represents a question in a quiz.

    Attributes:
        id (int): The unique identifier for the question.
        title (str): The text of the question. This field is required.
        quiz_id (int): The identifier of the quiz to which the question belongs. This field is optional.
        company_id (int): The identifier of the company associated with the question. This field is optional.
        created_at (datetime): The timestamp when the question was created. Defaults to the current time.
        updated_at (datetime): The timestamp when the question was last updated. Updates automatically on modification.

    Relationships:
        quiz (relationship): The quiz to which the question belongs.
        company (relationship): The company associated with the question.
        answers (relationship): The list of answers associated with the question.
        answered_questions (relationship): The list of answered questions related to the question.
    """

    __tablename__ = "question"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    quiz_id = Column(Integer, ForeignKey("quiz.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    quiz = relationship("Quiz", back_populates="questions")
    company = relationship("Company", back_populates="questions")
    answers = relationship(
        "Answer", back_populates="question", cascade="all, delete-orphan"
    )
    answered_questions = relationship("AnsweredQuestion", back_populates="question")
