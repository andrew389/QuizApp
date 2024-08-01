from typing import Optional, Dict
from pydantic import BaseModel, Field


class AnsweredQuestionBase(BaseModel):
    """
    Base schema for an answered question.
    """

    id: Optional[int] = Field(
        None,
        description="The unique identifier of the answered question. Default is None.",
    )
    user_id: int = Field(
        ..., description="The ID of the user who answered the question."
    )
    company_id: int = Field(
        ..., description="The ID of the company associated with the question."
    )
    quiz_id: int = Field(..., description="The ID of the quiz containing the question.")
    question_id: int = Field(..., description="The ID of the question.")
    answer_id: int = Field(..., description="The ID of the answer chosen by the user.")
    answer_text: str = Field(
        ..., description="The text of the answer chosen by the user."
    )
    is_correct: bool = Field(
        ..., description="Flag indicating if the chosen answer is correct."
    )


class AnsweredQuestionUpdate(AnsweredQuestionBase):
    """
    Schema for updating an answered question.
    Inherits all attributes from AnsweredQuestionBase.
    """

    pass


class SendAnsweredQuiz(BaseModel):
    """
    Schema for sending a quiz with answered questions.
    """

    answers: Dict[int, int] = Field(
        ...,
        description="A dictionary where the key is the question ID and the value is the answer ID.",
    )
