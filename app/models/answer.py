from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.pg_db import Base


class Answer(Base):
    """
    Represents an answer to a question in the system.

    Attributes:
        id (int): The unique identifier for the answer.
        text (str): The text of the answer. This field is required.
        is_correct (bool): Indicates whether the answer is correct. Defaults to False.
        question_id (int): The identifier of the question that this answer is related to. This field is optional.
        company_id (int): The identifier of the company associated with the answer. This field is optional.
        created_at (datetime): The timestamp when the answer record was created. Defaults to the current time.
        updated_at (datetime): The timestamp when the answer record was last updated. Updates automatically on modification.

    Relationships:
        question (relationship): The question to which this answer belongs.
        company (relationship): The company associated with this answer.
        answered_questions (relationship): The list of answered questions related to this answer.
    """

    __tablename__ = "answer"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=True, default=False)
    question_id = Column(Integer, ForeignKey("question.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    question = relationship("Question", back_populates="answers")
    company = relationship("Company", back_populates="answers")
    answered_questions = relationship("AnsweredQuestion", back_populates="answer")
