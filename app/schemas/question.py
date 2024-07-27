from typing import Optional, List, Union, Set

from pydantic import BaseModel, field_validator

from app.schemas.answer import AnswerBase, AnswerResponse
from app.schemas.pagination import PaginationLinks


class QuestionBase(BaseModel):
    id: Optional[int] = None
    title: str
    quiz_id: Optional[int] = None
    answers: Optional[Set[int]] = None
    company_id: int


class QuestionCreate(BaseModel):
    title: str
    answers: Set[int]
    company_id: int

    @field_validator("answers", mode="before")
    def validate_answers_length(cls, answers):
        if len(answers) < 2 or len(answers) > 4:
            raise ValueError("The list of answers must contain between 2 and 4 items.")
        return answers

    class Config:
        from_attributes = True


class QuestionUpdate(BaseModel):
    title: str


class QuestionResponse(BaseModel):
    id: int
    title: str
    answers: List[Union[AnswerBase, AnswerResponse]] = []

    @field_validator("answers", mode="before")
    def validate_answers_length(cls, answers):
        if len(answers) < 2 or len(answers) > 4:
            raise ValueError("The list of answers must contain between 2 and 4 items.")
        return answers

    class Config:
        from_attributes = True


class QuestionResponseForList(BaseModel):
    id: int
    title: str
    quiz_id: Optional[int] = None
    company_id: int

    class Config:
        from_attributes = True


class QuestionsListResponse(BaseModel):
    links: PaginationLinks
    questions: List[QuestionResponseForList] = []
    total: int
