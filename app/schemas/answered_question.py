from typing import Optional, Dict
from pydantic import BaseModel


class AnsweredQuestionBase(BaseModel):
    """
    Base schema for an answered question.

    Attributes:
        id (Optional[int]): The unique identifier of the answered question. Default is None.
        user_id (int): The ID of the user who answered the question.
        company_id (int): The ID of the company associated with the question.
        quiz_id (int): The ID of the quiz containing the question.
        question_id (int): The ID of the question.
        answer_id (int): The ID of the answer chosen by the user.
        answer_text (str): The text of the answer chosen by the user.
        is_correct (bool): Flag indicating if the chosen answer is correct.
    """

    id: Optional[int] = None
    user_id: int
    company_id: int
    quiz_id: int
    question_id: int
    answer_id: int
    answer_text: str
    is_correct: bool


class AnsweredQuestionUpdate(AnsweredQuestionBase):
    """
    Schema for updating an answered question.
    Inherits all attributes from AnsweredQuestionBase.
    """

    pass


class SendAnsweredQuiz(BaseModel):
    """
    Schema for sending a quiz with answered questions.

    Attributes:
        answers (Dict[int, int]): A dictionary where the key is the question ID and the value is the answer ID.
    """

    answers: Dict[int, int]
