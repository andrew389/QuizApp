from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


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


class Company(Base):
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
    quizzes = relationship(
        "Quiz", back_populates="company", cascade="all, delete-orphan"
    )
    questions = relationship(
        "Question", back_populates="company", cascade="all, delete-orphan"
    )
    answers = relationship(
        "Answer", back_populates="company", cascade="all, delete-orphan"
    )


class Invitation(Base):
    __tablename__ = "invitation"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    sender_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    company_id = Column(
        Integer, ForeignKey("company.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )
    status = Column(String, default="pending")

    sender = relationship(
        "User", foreign_keys=[sender_id], back_populates="sent_invitations"
    )
    receiver = relationship(
        "User", foreign_keys=[receiver_id], back_populates="received_invitations"
    )
    company = relationship("Company", back_populates="invitations")


class Member(Base):
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


class Quiz(Base):
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


class Question(Base):
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
