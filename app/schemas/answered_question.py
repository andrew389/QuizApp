from typing import Optional, Dict

from pydantic import BaseModel


class AnsweredQuestionBase(BaseModel):
    id: Optional[int] = None
    user_id: int
    company_id: int
    quiz_id: int
    question_id: int
    answer_id: int
    answer_text: str
    is_correct: bool


class AnsweredQuestionUpdate(AnsweredQuestionBase):
    pass


class SendAnsweredQuiz(BaseModel):
    answers: Dict[int, int]
