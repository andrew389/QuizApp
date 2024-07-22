from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.pg_db import Base


class AnsweredQuestion(Base):
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
