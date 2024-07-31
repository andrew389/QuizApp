from typing import Optional, List

from pydantic import BaseModel, field_validator

from app.schemas.pagination import PaginationLinks
from app.schemas.question import QuestionResponse


class QuizBase(BaseModel):
    """
    Base schema for a quiz.

    Attributes:
        id (Optional[int]): The unique identifier of the quiz.
        title (str): The title of the quiz.
        description (Optional[str]): The description of the quiz.
        frequency (int): The frequency of the quiz.
        company_id (int): The unique identifier of the associated company.
        questions (List[int]): A list of unique identifiers for the associated questions.
    """

    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    frequency: int = 0
    company_id: int
    questions: List[int] = []


class QuizCreate(BaseModel):
    """
    Schema for creating a quiz.

    Attributes:
        title (str): The title of the quiz.
        description (Optional[str]): The description of the quiz.
        frequency (int): The frequency of the quiz.
        company_id (int): The unique identifier of the associated company.
        questions (List[int]): A list of unique identifiers for the associated questions.
    """

    title: str
    description: Optional[str] = None
    frequency: int = 0
    company_id: int
    questions: List[int] = []

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

    Attributes:
        title (str): The title of the quiz.
        description (str): The description of the quiz.
    """

    title: str
    description: str


class QuizResponse(BaseModel):
    """
    Schema for a quiz response.

    Attributes:
        title (str): The title of the quiz.
        description (str): The description of the quiz.
        frequency (int): The frequency of the quiz.
        questions (List[QuestionResponse]): A list of responses for the associated questions.
    """

    title: str
    description: str
    frequency: int
    questions: List[QuestionResponse] = []

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

    Attributes:
        id (int): The unique identifier of the quiz.
        title (str): The title of the quiz.
        description (str): The description of the quiz.
        frequency (int): The frequency of the quiz.
        company_id (int): The unique identifier of the associated company.
    """

    id: int
    title: str
    description: str
    frequency: int
    company_id: int

    class Config:
        from_attributes = True


class QuizzesListResponse(BaseModel):
    """
    Schema for a list of quizzes.

    Attributes:
        links (PaginationLinks): The pagination links.
        quizzes (List[QuizResponseForList]): A list of quiz responses.
        total (int): The total number of quizzes.
    """

    links: PaginationLinks
    quizzes: List[QuizResponseForList] = []
    total: int
