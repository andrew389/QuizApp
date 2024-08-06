from fastapi import APIRouter, UploadFile, File
from app.core.dependencies import (
    UOWDep,
    QuizServiceDep,
    DataImportServiceDep,
    CurrentUserDep,
)
from app.core.logger import logger
from app.exceptions.base import (
    FetchingException,
    CreatingException,
    UpdatingException,
    DeletingException,
    ImportingException,
)
from app.models.user import User
from app.schemas.quiz import (
    QuizResponse,
    QuizCreate,
    QuizBase,
    QuizUpdate,
)

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.post("/", response_model=QuizBase)
async def create_quiz(
    quiz: QuizCreate,
    uow: UOWDep,
    quiz_service: QuizServiceDep,
    current_user: CurrentUserDep,
):
    """
    Creates a new quiz.

    Args:
        quiz (QuizCreate): Data to create a new quiz.
        uow (UOWDep): Unit of Work dependency for database operations.
        quiz_service (QuizServiceDep): Service for managing quizzes.
        current_user (User): The currently authenticated user.

    Returns:
        QuizBase: The created quiz details.

    Raises:
        CreatingException: If an error occurs during quiz creation.
    """
    try:
        return await quiz_service.create_quiz(uow, quiz, current_user.id)
    except Exception as e:
        logger.error(f"Error creating quiz: {e}")
        raise CreatingException()


@router.put("/{quiz_id}", response_model=QuizBase)
async def update_quiz(
    quiz_id: int,
    quiz: QuizUpdate,
    uow: UOWDep,
    quiz_service: QuizServiceDep,
    current_user: CurrentUserDep,
):
    """
    Updates an existing quiz.

    Args:
        quiz_id (int): The ID of the quiz to update.
        quiz (QuizUpdate): Data to update the quiz.
        uow (UOWDep): Unit of Work dependency for database operations.
        quiz_service (QuizServiceDep): Service for managing quizzes.
        current_user (User): The currently authenticated user.

    Returns:
        QuizBase: The updated quiz details.

    Raises:
        UpdatingException: If an error occurs during quiz update.
    """
    try:
        return await quiz_service.update_quiz(uow, quiz_id, quiz, current_user.id)
    except Exception as e:
        logger.error(f"Error updating quiz: {e}")
        raise UpdatingException()


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz_by_id(
    quiz_id: int,
    uow: UOWDep,
    quiz_service: QuizServiceDep,
    current_user: CurrentUserDep,
):
    """
    Retrieves a quiz by its ID.

    Args:
        quiz_id (int): The ID of the quiz to retrieve.
        uow (UOWDep): Unit of Work dependency for database operations.
        quiz_service (QuizServiceDep): Service for managing quizzes.
        current_user (User): The currently authenticated user.

    Returns:
        QuizResponse: The details of the retrieved quiz.

    Raises:
        FetchingException: If an error occurs during fetching the quiz.
    """
    try:
        return await quiz_service.get_quiz_by_id(uow, quiz_id, current_user.id)
    except Exception as e:
        logger.error(f"Error fetching quiz: {e}")
        raise FetchingException()


@router.delete("/{quiz_id}", response_model=QuizBase)
async def delete_quiz(
    quiz_id: int,
    uow: UOWDep,
    quiz_service: QuizServiceDep,
    current_user: CurrentUserDep,
):
    """
    Deletes a quiz by its ID.

    Args:
        quiz_id (int): The ID of the quiz to delete.
        uow (UOWDep): Unit of Work dependency for database operations.
        quiz_service (QuizServiceDep): Service for managing quizzes.
        current_user (User): The currently authenticated user.

    Returns:
        QuizBase: The details of the deleted quiz.

    Raises:
        DeletingException: If an error occurs during quiz deletion.
    """
    try:
        return await quiz_service.delete_quiz(uow, quiz_id, current_user.id)
    except Exception as e:
        logger.error(f"Error deleting quiz: {e}")
        raise DeletingException()


@router.post("/import", response_model=dict)
async def import_quizzes(
    uow: UOWDep,
    data_import_service: DataImportServiceDep,
    current_user: CurrentUserDep,
    file: UploadFile = File(...),
):
    """
    Imports quiz data from an Excel file.

    Args:
        uow (UOWDep): Unit of Work dependency for database operations.
        data_import_service (DataImportServiceDep): Service for importing quiz data.
        file (UploadFile): The Excel file containing quiz data.
        current_user (User): The currently authenticated user.

    Returns:
        dict: A dictionary with a message indicating success.

    Raises:
        ImportingException: If an error occurs during importing quizzes.
    """
    try:
        await data_import_service.import_data(file, uow, current_user.id)
        return {"message": "Quizzes imported successfully"}
    except Exception as e:
        logger.error(f"{e}")
        raise ImportingException()
