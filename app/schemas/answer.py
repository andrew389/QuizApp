from typing import Optional, List

from pydantic import BaseModel


class AnswerBase(BaseModel):
    id: Optional[int] = None
    text: str
    is_correct: bool = False
    company_id: int
    question_id: Optional[int] = None


class AnswerCreate(BaseModel):
    text: str
    is_correct: bool = False
    company_id: int


class AnswerUpdate(BaseModel):
    text: str
    is_correct: bool


class AnswerResponse(BaseModel):
    id: Optional[int] = None
    text: str
    company_id: int
    question_id: Optional[int] = None


class AnswersListResponse(BaseModel):
    answers: List[AnswerBase] = []
    total: int
