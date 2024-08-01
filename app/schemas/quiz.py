from typing import Optional, List

from pydantic import BaseModel, Field, field_validator

from app.schemas.pagination import PaginationLinks
from app.schemas.question import QuestionResponse


class QuizBase(BaseModel):
    """
    Base schema for a quiz.
    """

    id: Optional[int] = Field(None, description="The unique identifier of the quiz.")
    title: str = Field(..., description="The title of the quiz.")
    description: Optional[str] = Field(None, description="The description of the quiz.")
    frequency: int = Field(0, description="The frequency of the quiz.")
    company_id: int = Field(
        ..., description="The unique identifier of the associated company."
    )
    questions: List[int] = Field(
        default_factory=list,
        description="A list of unique identifiers for the associated questions.",
    )


class QuizCreate(BaseModel):
    """
    Schema for creating a quiz.
    """

    title: str = Field(..., description="The title of the quiz.")
    description: Optional[str] = Field(None, description="The description of the quiz.")
    frequency: int = Field(0, description="The frequency of the quiz.")
    company_id: int = Field(
        ..., description="The unique identifier of the associated company."
    )
    questions: List[int] = Field(
        default_factory=list,
        description="A list of unique identifiers for the associated questions.",
    )

    @field_validator("questions", mode="before")
    def validate_questions_length(cls, questions):
        """
        Validates the length of the questions list.

        Args:
            questions (List[int]): A list of unique identifiers for the questions.

        Raises:
            ValueError: If the list contains fewer than 2 items.

        Returns:
            List[int]: The validated list of questions.
        """
        if len(questions) < 2:
            raise ValueError("The list of questions must contain at least 2 items.")
        return questions


class QuizUpdate(BaseModel):
    """
    Schema for updating a quiz.
    """

    title: str = Field(..., description="The title of the quiz.")
    description: str = Field(..., description="The description of the quiz.")


class QuizResponse(BaseModel):
    """
    Schema for a quiz response.
    """

    title: str = Field(..., description="The title of the quiz.")
    description: str = Field(..., description="The description of the quiz.")
    frequency: int = Field(..., description="The frequency of the quiz.")
    questions: List[QuestionResponse] = Field(
        default_factory=list,
        description="A list of responses for the associated questions.",
    )

    @field_validator("questions", mode="before")
    def validate_questions_length(cls, questions):
        """
        Validates the length of the questions list.

        Args:
            questions (List[QuestionResponse]): A list of responses for the associated questions.

        Raises:
            ValueError: If the list contains fewer than 2 items.

        Returns:
            List[QuestionResponse]: The validated list of questions.
        """
        if len(questions) < 2:
            raise ValueError("The list of questions must contain at least 2 items.")
        return questions


class QuizResponseForList(BaseModel):
    """
    Schema for a quiz response in a list.
    """

    id: int = Field(..., description="The unique identifier of the quiz.")
    title: str = Field(..., description="The title of the quiz.")
    description: str = Field(..., description="The description of the quiz.")
    frequency: int = Field(..., description="The frequency of the quiz.")
    company_id: int = Field(
        ..., description="The unique identifier of the associated company."
    )

    class Config:
        from_attributes = True


class QuizzesListResponse(BaseModel):
    """
    Schema for a list of quizzes.
    """

    links: PaginationLinks = Field(..., description="The pagination links.")
    quizzes: List[QuizResponseForList] = Field(
        default_factory=list, description="A list of quiz responses."
    )
    total: int = Field(..., description="The total number of quizzes.")
