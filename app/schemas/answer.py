from typing import Optional

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
    is_correct: bool = False
