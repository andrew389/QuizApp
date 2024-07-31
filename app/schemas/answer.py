from typing import Optional, List
from pydantic import BaseModel
from app.schemas.pagination import PaginationLinks


class AnswerBase(BaseModel):
    """
    Base schema for an Answer.

    Attributes:
        id (Optional[int]): The unique identifier of the answer. Default is None.
        text (str): The text content of the answer.
        is_correct (bool): Flag indicating if the answer is correct. Default is False.
        company_id (int): The ID of the company associated with the answer.
        question_id (Optional[int]): The ID of the question associated with the answer. Default is None.
    """

    id: Optional[int] = None
    text: str
    is_correct: bool = False
    company_id: int
    question_id: Optional[int] = None

    class Config:
        from_attributes = True


class AnswerCreate(BaseModel):
    """
    Schema for creating a new Answer.

    Attributes:
        text (str): The text content of the answer.
        is_correct (bool): Flag indicating if the answer is correct. Default is False.
        company_id (int): The ID of the company associated with the answer.
    """

    text: str
    is_correct: bool = False
    company_id: int


class AnswerUpdate(BaseModel):
    """
    Schema for updating an existing Answer.

    Attributes:
        text (str): The text content of the answer.
        company_id (int): The ID of the company associated with the answer.
        is_correct (bool): Flag indicating if the answer is correct.
    """

    text: str
    company_id: int
    is_correct: bool


class AnswerResponse(BaseModel):
    """
    Response schema for an Answer.

    Attributes:
        id (Optional[int]): The unique identifier of the answer. Default is None.
        text (str): The text content of the answer.
        company_id (int): The ID of the company associated with the answer.
        question_id (Optional[int]): The ID of the question associated with the answer. Default is None.
    """

    id: Optional[int] = None
    text: str
    company_id: int
    question_id: Optional[int] = None

    class Config:
        from_attributes = True


class AnswersListResponse(BaseModel):
    """
    Response schema for a list of Answers with pagination.

    Attributes:
        links (PaginationLinks): Pagination links for navigating through the list.
        answers (List[AnswerBase]): A list of AnswerBase schemas representing the answers.
        total (int): The total number of answers.
    """

    links: PaginationLinks
    answers: List[AnswerBase] = []
    total: int
