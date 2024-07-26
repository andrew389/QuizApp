from typing import Optional, List

from pydantic import BaseModel, field_validator

from app.schemas.question import QuestionResponse


class QuizBase(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    frequency: int = 0
    company_id: int
    questions: List[int] = []


class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = None
    frequency: int = 0
    company_id: int
    questions: List[int] = []

    @field_validator("questions", mode="before")
    def validate_questions_length(cls, questions):
        if len(questions) < 2:
            raise ValueError("The list of questions must contain at least 2 items.")
        return questions


class QuizUpdate(BaseModel):
    title: str
    description: str


class QuizResponse(BaseModel):
    title: str
    description: str
    frequency: int
    questions: List[QuestionResponse] = []

    @field_validator("questions", mode="before")
    def validate_questions_length(cls, questions):
        if len(questions) < 2:
            raise ValueError("The list of questions must contain at least 2 items.")
        return questions


class QuizResponseForList(BaseModel):
    id: int
    title: str
    description: str
    frequency: int
    company_id: int

    class Config:
        from_attributes = True


class QuizzesListResponse(BaseModel):
    quizzes: List[QuizResponseForList] = []
    total: int
