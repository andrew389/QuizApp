from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.pg_db import Base


class Answer(Base):
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
