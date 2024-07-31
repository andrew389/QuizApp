from typing import Optional, List, Union, Set

from pydantic import BaseModel, field_validator

from app.schemas.answer import AnswerBase, AnswerResponse
from app.schemas.pagination import PaginationLinks


class QuestionBase(BaseModel):
    """
    Base schema for a question.

    Attributes:
        id (Optional[int]): The unique identifier of the question.
        title (str): The title of the question.
        quiz_id (Optional[int]): The unique identifier of the associated quiz.
        answers (Optional[Set[int]]): A set of unique identifiers for the associated answers.
        company_id (int): The unique identifier of the associated company.
    """

    id: Optional[int] = None
    title: str
    quiz_id: Optional[int] = None
    answers: Optional[Set[int]] = None
    company_id: int


class QuestionCreate(BaseModel):
    """
    Schema for creating a question.

    Attributes:
        title (str): The title of the question.
        answers (Set[int]): A set of unique identifiers for the associated answers.
        company_id (int): The unique identifier of the associated company.
    """

    title: str
    answers: Set[int] = []

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

    Attributes:
        title (str): The title of the question.
    """

    title: str


class QuestionResponse(BaseModel):
    """
    Schema for a question response.

    Attributes:
        id (int): The unique identifier of the question.
        title (str): The title of the question.
        answers (List[Union[AnswerBase, AnswerResponse]]): A list of answers associated with the question.
    """

    id: int
    title: str
    answers: List[Union[AnswerBase, AnswerResponse]] = []

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

    Attributes:
        id (int): The unique identifier of the question.
        title (str): The title of the question.
        quiz_id (Optional[int]): The unique identifier of the associated quiz.
        company_id (int): The unique identifier of the associated company.
    """

    id: int
    title: str
    quiz_id: Optional[int] = None
    company_id: int

    class Config:
        from_attributes = True


class QuestionsListResponse(BaseModel):
    """
    Schema for a list of questions.

    Attributes:
        links (PaginationLinks): The pagination links.
        questions (List[QuestionResponseForList]): A list of question responses.
        total (int): The total number of questions.
    """

    links: PaginationLinks
    questions: List[QuestionResponseForList] = []
    total: int
