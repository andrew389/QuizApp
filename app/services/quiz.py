from fastapi import Request
from app.core.logger import logger
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException
from app.schemas.question import QuestionResponse
from app.schemas.quiz import (
    QuizCreate,
    QuizResponse,
    QuizBase,
    QuizUpdate,
    QuizzesListResponse,
    QuizResponseForList,
)
from app.services.notification import NotificationService
from app.services.question import QuestionService
from app.uow.unitofwork import UnitOfWork
from app.utils.user import get_pagination_urls, filter_data


class QuizService:
    """
    Service for handling quizzes within a company.

    This service provides functionalities for creating, updating, retrieving, and deleting quizzes. It also manages
    the association of quizzes with questions and handles permission checks to ensure that users have appropriate
    rights to perform these operations.

    Methods:
        - create_quiz: Creates a new quiz and associates it with the provided questions. Notifies the company members
          about the new quiz.
        - update_quiz: Updates an existing quiz with new details. Checks for user permissions before applying updates.
        - get_quiz_by_id: Retrieves a quiz by its ID along with its associated questions. Ensures that the user has
          the necessary permissions to view the quiz.
        - get_quizzes: Retrieves a list of quizzes for a specific company, with pagination support. Checks user
          permissions for accessing the list of quizzes.
        - delete_quiz: Deletes a quiz and disassociates its questions. Ensures that the user has permission to delete
          the quiz and handles the removal of questions associated with the quiz.
    """

    @staticmethod
    async def create_quiz(
        uow: UnitOfWork, quiz: QuizCreate, current_user_id: int
    ) -> QuizBase:
        """
        Create a new quiz and associate it with questions.

        Args:
            uow (UnitOfWork): The unit of work for database transactions.
            quiz (QuizCreate): The details of the quiz to create.
            current_user_id (int): The ID of the user creating the quiz.

        Returns:
            QuizBase: The created quiz.

        Raises:
            UnAuthorizedException: If the user lacks permission to create the quiz.
            NotFoundException: If any of the specified questions are not found.
        """
        from app.services.member_management import MemberManagement

        async with uow:
            has_permission = await MemberManagement.check_is_user_have_permission(
                uow, current_user_id, quiz.company_id
            )
            if not has_permission:
                logger.error(
                    f"User {current_user_id} lacks permission to create quiz in company {quiz.company_id}."
                )
                raise UnAuthorizedException()

            new_quiz = await uow.quiz.add_one(
                quiz.model_dump(exclude={"questions", "id"})
            )

            for question_id in quiz.questions:
                existing_question = await uow.question.find_one(
                    id=question_id, quiz_id=None
                )
                if existing_question:
                    await uow.question.edit_one(question_id, {"quiz_id": new_quiz.id})
                else:
                    logger.error(f"Question with ID {question_id} not found.")
                    raise NotFoundException()

            await NotificationService.send_notifications(
                uow, quiz.company_id, f"A new quiz has been created: {quiz.title}"
            )

            quiz_data = filter_data(new_quiz)

            return QuizBase.model_validate(quiz_data)

    @staticmethod
    async def update_quiz(
        uow: UnitOfWork, quiz_id: int, quiz: QuizUpdate, current_user_id: int
    ) -> QuizBase:
        """
        Update an existing quiz.

        Args:
            uow (UnitOfWork): The unit of work for database transactions.
            quiz_id (int): The ID of the quiz to update.
            quiz (QuizUpdate): The updated quiz details.
            current_user_id (int): The ID of the user updating the quiz.

        Returns:
            QuizBase: The updated quiz.

        Raises:
            NotFoundException: If the quiz to update is not found.
            UnAuthorizedException: If the user lacks permission to update the quiz.
        """
        from app.services.member_management import MemberManagement

        async with uow:
            quiz_to_update = await uow.quiz.find_one(id=quiz_id)
            if not quiz_to_update:
                logger.error(f"Quiz with ID {quiz_id} not found.")
                raise NotFoundException()

            has_permission = await MemberManagement.check_is_user_have_permission(
                uow, current_user_id, quiz_to_update.company_id
            )
            if not has_permission:
                logger.error(
                    f"User {current_user_id} lacks permission to update quiz {quiz_id}."
                )
                raise UnAuthorizedException()

            updated_quiz = await uow.quiz.edit_one(quiz_id, quiz.model_dump())

            quiz_data = filter_data(updated_quiz)

            return QuizBase.model_validate(quiz_data)

    @staticmethod
    async def get_quiz_by_id(
        uow: UnitOfWork, quiz_id: int, current_user_id: int
    ) -> QuizResponse:
        """
        Retrieve a quiz by its ID, including associated questions.

        Args:
            uow (UnitOfWork): The unit of work for database transactions.
            quiz_id (int): The ID of the quiz to retrieve.
            current_user_id (int): The ID of the user requesting the quiz.

        Returns:
            QuizResponse: The quiz details including its questions.

        Raises:
            NotFoundException: If the quiz or its questions are not found.
            UnAuthorizedException: If the user lacks permission to view the quiz.
            FetchingException: If the number of questions is less than 2.
        """
        from app.services.member_management import MemberManagement

        async with uow:
            quiz = await uow.quiz.find_one(id=quiz_id)
            if not quiz:
                logger.error(f"Quiz with ID {quiz_id} not found.")
                raise NotFoundException()

            questions = await uow.question.find_all_by_quiz_id(quiz_id=quiz_id)

            has_permission = await MemberManagement.check_is_user_member_or_higher(
                uow, current_user_id, quiz.company_id
            )

            if not has_permission:
                logger.error(
                    f"User {current_user_id} lacks permission to view quiz {quiz_id}."
                )
                raise UnAuthorizedException()

            quiz_data = {
                "title": quiz.title,
                "description": quiz.description,
                "frequency": quiz.frequency,
                "questions": [
                    QuestionResponse(
                        **(
                            await QuestionService.get_question_by_id(
                                uow, question.id, current_user_id
                            )
                        ).__dict__
                    )
                    for question in questions
                ],
            }

            return QuizResponse.model_validate(quiz_data)

    @staticmethod
    async def get_quizzes(
        uow: UnitOfWork,
        company_id: int,
        current_user_id: int,
        request: Request,
        skip: int = 0,
        limit: int = 10,
    ) -> QuizzesListResponse:
        """
        Retrieve a list of quizzes for a specific company.

        Args:
            uow (UnitOfWork): The unit of work for database transactions.
            company_id (int): The ID of the company.
            current_user_id (int): The ID of the user requesting the list.
            request (Request): request from endpoint to get base url./
            skip (int, optional): Number of quizzes to skip (default is 0).
            limit (int, optional): Maximum number of quizzes to return (default is 10).

        Returns:
            QuizzesListResponse: A list of quizzes and the total count.

        Raises:
            UnAuthorizedException: If the user lacks permission to view quizzes for the company.
        """
        from app.services.member_management import MemberManagement

        async with uow:
            has_permission = await MemberManagement.check_is_user_member_or_higher(
                uow, current_user_id, company_id
            )
            if not has_permission:
                logger.error(
                    f"User {current_user_id} lacks permission to view quizzes for company {company_id}."
                )
                raise UnAuthorizedException()

            quizzes = await uow.quiz.find_all(skip=skip, limit=limit)

            total_quizzes = await uow.quiz.count()
            links = get_pagination_urls(request, skip, limit, total_quizzes)

            quizzes_list = QuizzesListResponse(
                links=links,
                quizzes=[QuizResponseForList.from_orm(quiz) for quiz in quizzes],
                total=total_quizzes,
            )

            return QuizzesListResponse.model_validate(quizzes_list)

    @staticmethod
    async def delete_quiz(
        uow: UnitOfWork, quiz_id: int, current_user_id: int
    ) -> QuizBase:
        """
        Delete a quiz and disassociate its questions.

        Args:
            uow (UnitOfWork): The unit of work for database transactions.
            quiz_id (int): The ID of the quiz to delete.
            current_user_id (int): The ID of the user requesting the deletion.

        Returns:
            QuizBase: The deleted quiz.

        Raises:
            NotFoundException: If the quiz to delete is not found.
            UnAuthorizedException: If the user lacks permission to delete the quiz.
        """
        from app.services.member_management import MemberManagement

        async with uow:
            quiz_to_delete = await uow.quiz.find_one(id=quiz_id)
            if not quiz_to_delete:
                logger.error(f"Quiz with ID {quiz_id} not found.")
                raise NotFoundException()

            has_permission = await MemberManagement.check_is_user_have_permission(
                uow, current_user_id, quiz_to_delete.company_id
            )
            if not has_permission:
                logger.error(
                    f"User {current_user_id} lacks permission to delete quiz {quiz_id}."
                )
                raise UnAuthorizedException()

            questions = await uow.question.find_all_by_quiz_id(quiz_id=quiz_id)
            for question in questions:
                await uow.question.edit_one(
                    question.id, {"quiz_id": None, "company_id": None}
                )

            deleted_quiz = await uow.quiz.delete_one(quiz_id)

            quiz_data = filter_data(deleted_quiz)

            return QuizBase.model_validate(quiz_data)
