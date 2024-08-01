from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.pagination import PaginationLinks


class AnswerBase(BaseModel):
    """
    Base schema for an Answer.
    """

    id: Optional[int] = Field(None, description="The unique identifier of the answer.")
    text: str = Field(..., description="The text content of the answer.")
    is_correct: bool = Field(
        False, description="Flag indicating if the answer is correct."
    )
    company_id: int = Field(
        ..., description="The ID of the company associated with the answer."
    )
    question_id: Optional[int] = Field(
        None, description="The ID of the question associated with the answer."
    )

    class Config:
        from_attributes = True


class AnswerCreate(BaseModel):
    """
    Schema for creating a new Answer.
    """

    text: str = Field(..., description="The text content of the answer.")
    is_correct: bool = Field(
        False, description="Flag indicating if the answer is correct."
    )
    company_id: int = Field(
        ..., description="The ID of the company associated with the answer."
    )


class AnswerUpdate(BaseModel):
    """
    Schema for updating an existing Answer.
    """

    text: str = Field(..., description="The text content of the answer.")
    company_id: int = Field(
        ..., description="The ID of the company associated with the answer."
    )
    is_correct: bool = Field(
        ..., description="Flag indicating if the answer is correct."
    )


class AnswerResponse(BaseModel):
    """
    Response schema for an Answer.
    """

    id: Optional[int] = Field(None, description="The unique identifier of the answer.")
    text: str = Field(..., description="The text content of the answer.")
    company_id: int = Field(
        ..., description="The ID of the company associated with the answer."
    )
    question_id: Optional[int] = Field(
        None, description="The ID of the question associated with the answer."
    )

    class Config:
        from_attributes = True


class AnswersListResponse(BaseModel):
    """
    Response schema for a list of Answers with pagination.
    """

    links: PaginationLinks = Field(
        ..., description="Pagination links for navigating through the list."
    )
    answers: List[AnswerBase] = Field(
        default_factory=list,
        description="A list of AnswerBase schemas representing the answers.",
    )
    total: int = Field(..., description="The total number of answers.")
