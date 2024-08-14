from typing import Optional, List, Union, Set

from pydantic import BaseModel, Field, field_validator

from app.schemas.answer import AnswerBase, AnswerResponse
from app.schemas.pagination import PaginationLinks


class QuestionBase(BaseModel):
    """
    Base schema for a question.
    """

    id: Optional[int] = Field(
        None, description="The unique identifier of the question."
    )
    title: str = Field(..., description="The title of the question.")
    quiz_id: Optional[int] = Field(
        None, description="The unique identifier of the associated quiz."
    )
    answers: Optional[Set[int]] = Field(
        None, description="A set of unique identifiers for the associated answers."
    )
    company_id: int = Field(
        ..., description="The unique identifier of the associated company."
    )


class QuestionCreate(BaseModel):
    """
    Schema for creating a question.
    """

    title: str = Field(..., description="The title of the question.")
    answers: Set[int] = Field(
        default_factory=set,
        description="A set of unique identifiers for the associated answers.",
    )
    company_id: int = Field(..., description="The unique identifier of the company.")

    @field_validator("answers", mode="before")
    def validate_answers_length(cls, answers):
        """
        Validates the length of the answers set.

        Args:
            answers (Set[int]): A set of unique identifiers for the answers.

        Raises:
            ValueError: If the set contains fewer than 2 or more than 4 items.

        Returns:
            Set[int]: The validated set of answers.
        """
        if len(answers) < 2 or len(answers) > 4:
            raise ValueError("The set of answers must contain between 2 and 4 items.")
        return answers

    class Config:
        from_attributes = True


class QuestionUpdate(BaseModel):
    """
    Schema for updating a question.
    """

    title: str = Field(..., description="The title of the question.")


class QuestionResponse(BaseModel):
    """
    Schema for a question response.
    """

    id: int = Field(..., description="The unique identifier of the question.")
    title: str = Field(..., description="The title of the question.")
    answers: List[Union[AnswerBase, AnswerResponse]] = Field(
        default_factory=list,
        description="A list of answers associated with the question.",
    )

    @field_validator("answers", mode="before")
    def validate_answers_length(cls, answers):
        """
        Validates the length of the answers list.

        Args:
            answers (List[Union[AnswerBase, AnswerResponse]]): A list of answers associated with the question.

        Raises:
            ValueError: If the list contains fewer than 2 or more than 4 items.

        Returns:
            List[Union[AnswerBase, AnswerResponse]]: The validated list of answers.
        """
        if len(answers) < 2 or len(answers) > 4:
            raise ValueError("The list of answers must contain between 2 and 4 items.")
        return answers

    class Config:
        from_attributes = True


class QuestionResponseForList(BaseModel):
    """
    Schema for a question response in a list.
    """

    id: int = Field(..., description="The unique identifier of the question.")
    title: str = Field(..., description="The title of the question.")
    quiz_id: Optional[int] = Field(
        None, description="The unique identifier of the associated quiz."
    )
    company_id: int = Field(
        ..., description="The unique identifier of the associated company."
    )

    class Config:
        from_attributes = True


class QuestionsListResponse(BaseModel):
    """
    Schema for a list of questions.
    """

    links: PaginationLinks = Field(..., description="The pagination links.")
    questions: List[QuestionResponseForList] = Field(
        default_factory=list, description="A list of question responses."
    )
    total: int = Field(..., description="The total number of questions.")
