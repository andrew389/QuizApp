from fastapi import Request

from app.core.logger import logger
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException
from app.schemas.answer import AnswerBase, AnswerResponse
from app.schemas.question import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionBase,
    QuestionsListResponse,
    QuestionResponseForList,
)
from app.uow.unitofwork import UnitOfWork
from app.utils.user import get_pagination_urls


class QuestionService:
    @staticmethod
    async def create_question(
        uow: UnitOfWork, question: QuestionCreate, current_user_id: int
    ) -> QuestionBase:
        """
        Create a new question and associate it with answers.

        Args:
            uow (UnitOfWork): The unit of work for database transactions.
            question (QuestionCreate): The details of the question to create.
            current_user_id (int): The ID of the user creating the question.

        Returns:
            QuestionBase: The created question.

        Raises:
            UnAuthorizedException: If the user lacks permission to create the question.
            NotFoundException: If any of the specified answers are not found.
        """
        from app.services.member_management import MemberManagement

        async with uow:
            has_permission = await MemberManagement.check_is_user_have_permission(
                uow, current_user_id, question.company_id
            )
            if not has_permission:
                logger.error(
                    f"User {current_user_id} lacks permission to create question in company {question.company_id}"
                )
                raise UnAuthorizedException()

            new_question = await uow.question.add_one(
                question.model_dump(exclude={"answers", "id"})
            )

            for answer_id in question.answers:
                existing_answer = await uow.answer.find_one(
                    id=answer_id, question_id=None
                )
                if existing_answer:
                    await uow.answer.edit_one(
                        answer_id, {"question_id": new_question.id}
                    )
                else:
                    logger.error(f"Answer with ID {answer_id} not found.")
                    raise NotFoundException()

            question_data = {
                key: value
                for key, value in new_question.__dict__.items()
                if not key.startswith("_")
            }

            return QuestionBase.model_validate(question_data)

    @staticmethod
    async def update_question(
        uow: UnitOfWork,
        question_id: int,
        question: QuestionUpdate,
        current_user_id: int,
    ) -> QuestionBase:
        """
        Update an existing question.

        Args:
            uow (UnitOfWork): The unit of work for database transactions.
            question_id (int): The ID of the question to update.
            question (QuestionUpdate): The updated question details.
            current_user_id (int): The ID of the user updating the question.

        Returns:
            QuestionBase: The updated question.

        Raises:
            NotFoundException: If the question to update is not found.
            UnAuthorizedException: If the user lacks permission to update the question.
        """
        async with uow:
            from app.services.member_management import MemberManagement

            question_to_update = await uow.question.find_one(id=question_id)

            if not question_to_update:
                logger.error(f"Question with ID {question_id} not found.")
                raise NotFoundException()

            has_permission = await MemberManagement.check_is_user_have_permission(
                uow, current_user_id, question_to_update.company_id
            )

            if not has_permission:
                logger.error(
                    f"User {current_user_id} lacks permission to update question {question_id}."
                )
                raise UnAuthorizedException()

            updated_question = await uow.question.edit_one(question_id, question.dict())

            question_data = {
                key: value
                for key, value in updated_question.__dict__.items()
                if not key.startswith("_")
            }

            return QuestionBase.model_validate(question_data)

    @staticmethod
    async def get_question_by_id(
        uow: UnitOfWork, question_id: int, current_user_id: int
    ) -> QuestionResponse:
        """
        Retrieve a question by its ID.

        Args:
            uow (UnitOfWork): The unit of work for database transactions.
            question_id (int): The ID of the question to retrieve.
            current_user_id (int): The ID of the user requesting the question.

        Returns:
            QuestionResponse: The question details including its answers.

        Raises:
            NotFoundException: If the question or its answers are not found.
            UnAuthorizedException: If the user lacks permission to view the question.
            FetchingException: If the number of answers is not between 2 and 4.
        """
        from app.services.member_management import MemberManagement

        async with uow:
            question = await uow.question.find_one(id=question_id)
            if not question:
                logger.error(f"Question with ID {question_id} not found.")
                raise NotFoundException()

            answers = await uow.answer.find_all_by_question_id(question_id=question_id)

            has_permission = await MemberManagement.check_is_user_have_permission(
                uow, current_user_id, question.company_id
            )

            if has_permission:
                question_data = {
                    "id": question_id,
                    "title": question.title,
                    "answers": [AnswerBase.from_orm(answer) for answer in answers],
                }
            else:
                question_data = {
                    "id": question_id,
                    "title": question.title,
                    "answers": [AnswerResponse.from_orm(answer) for answer in answers],
                }

            return QuestionResponse.model_validate(question_data)

    @staticmethod
    async def get_questions(
        uow: UnitOfWork,
        request: Request,
        company_id: int,
        current_user_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> QuestionsListResponse:
        """
        Retrieve a list of questions for a specific company.

        Args:
            uow (UnitOfWork): The unit of work for database transactions.
            company_id (int): The ID of the company.
            current_user_id (int): The ID of the user requesting the list.
            request (Request): request from endpoint to get base url.*
            skip (int, optional): Number of questions to skip (default is 0).
            limit (int, optional): Maximum number of questions to return (default is 10).

        Returns:
            QuestionsListResponse: A list of questions and the total count.

        Raises:
            UnAuthorizedException: If the user lacks permission to view questions for the company.
        """
        from app.services.member_management import MemberManagement

        async with uow:
            has_permission = await MemberManagement.check_is_user_have_permission(
                uow, current_user_id, company_id
            )

            if not has_permission:
                logger.error(
                    f"User {current_user_id} lacks permission to view questions for company {company_id}."
                )
                raise UnAuthorizedException()

            questions = await uow.question.find_all(skip=skip, limit=limit)

            total_questions = await uow.question.count()

            links = get_pagination_urls(request, skip, limit, total_questions)

            question_list = QuestionsListResponse(
                links=links,
                questions=[
                    QuestionResponseForList.from_orm(question) for question in questions
                ],
                total=total_questions,
            )

            return QuestionsListResponse.model_validate(question_list)

    @staticmethod
    async def delete_question(
        uow: UnitOfWork, question_id: int, current_user_id: int
    ) -> QuestionBase:
        """
        Delete a question and disassociate its answers.

        Args:
            uow (UnitOfWork): The unit of work for database transactions.
            question_id (int): The ID of the question to delete.
            current_user_id (int): The ID of the user requesting the deletion.

        Returns:
            QuestionBase: The deleted question.

        Raises:
            NotFoundException: If the question to delete is not found.
            UnAuthorizedException: If the user lacks permission to delete the question.
        """
        from app.services.member_management import MemberManagement

        async with uow:
            question_to_delete = await uow.question.find_one(id=question_id)

            if not question_to_delete:
                logger.error(f"Question with ID {question_id} not found.")
                raise NotFoundException()

            has_permission = await MemberManagement.check_is_user_have_permission(
                uow, current_user_id, question_to_delete.company_id
            )

            if not has_permission:
                logger.error(
                    f"User {current_user_id} lacks permission to delete question {question_id}."
                )
                raise UnAuthorizedException()

            answers = await uow.answer.find_all_by_question_id(question_id=question_id)

            for answer in answers:
                await uow.answer.edit_one(
                    answer.id, {"question_id": None, "company_id": None}
                )

            deleted_question = await uow.question.delete_one(question_id)

            question_data = {
                key: value
                for key, value in deleted_question.__dict__.items()
                if not key.startswith("_")
            }

            return QuestionBase.model_validate(question_data)
