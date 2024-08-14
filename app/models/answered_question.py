from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.pg_db import Base


class AnsweredQuestion(Base):
    """
    Represents an answered question in the system.

    Attributes:
        id (int): The unique identifier for the answered question.
        user_id (int): The identifier of the user who answered the question.
        company_id (int): The identifier of the company associated with the answered question.
        quiz_id (int): The identifier of the quiz in which the question was answered.
        question_id (int): The identifier of the question that was answered.
        answer_id (int): The identifier of the answer provided by the user.
        answer_text (str): The text of the answer provided by the user.
        is_correct (bool): Indicates whether the provided answer is correct.
        created_at (datetime): The timestamp when the answered question record was created. Defaults to the current time.

    Relationships:
        user (relationship): The user who answered the question.
        company (relationship): The company associated with the answered question.
        quiz (relationship): The quiz that contains the answered question.
        question (relationship): The question that was answered.
        answer (relationship): The answer that was provided by the user.
    """

    __tablename__ = "answered_question"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quiz.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("question.id"), nullable=False)
    answer_id = Column(Integer, ForeignKey("answer.id"), nullable=False)
    answer_text = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)

    user = relationship("User", back_populates="answered_questions")
    company = relationship("Company", back_populates="answered_questions")
    quiz = relationship("Quiz", back_populates="answered_questions")
    question = relationship("Question", back_populates="answered_questions")
    answer = relationship("Answer", back_populates="answered_questions")
