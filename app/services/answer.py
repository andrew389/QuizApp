from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException
from app.schemas.answer import (
    AnswerUpdate,
    AnswerCreate,
    AnswerBase,
    AnswersListResponse,
)
from app.uow.unitofwork import UnitOfWork


class AnswerService:
    @staticmethod
    async def create_answer(
        uow: UnitOfWork, answer: AnswerCreate, current_user_id: int
    ) -> AnswerBase:
        """
        Create a new answer.

        Args:
            uow (UnitOfWork): The unit of work object for database transactions.
            answer (AnswerCreate): The data for creating a new answer.
            current_user_id (int): The ID of the user creating the answer.

        Returns:
            AnswerBase: The created answer.

        Raises:
            UnAuthorizedException: If the user does not have permission.
        """
        from app.services.member_management import MemberManagement

        async with uow:
            has_permission = await MemberManagement.check_is_user_have_permission(
                uow, current_user_id, answer.company_id
            )
            if not has_permission:
                raise UnAuthorizedException()

            new_answer = await uow.answer.add_one(answer.dict(exclude={"id"}))
            return AnswerBase(**new_answer.__dict__)

    @staticmethod
    async def update_answer(
        uow: UnitOfWork, answer_id: int, answer: AnswerUpdate, current_user_id: int
    ) -> AnswerBase:
        """
        Update an existing answer.

        Args:
            uow (UnitOfWork): The unit of work object for database transactions.
            answer_id (int): The ID of the answer to update.
            answer (AnswerUpdate): The updated data for the answer.
            current_user_id (int): The ID of the user performing the update.

        Returns:
            AnswerBase: The updated answer.

        Raises:
            UnAuthorizedException: If the user does not have permission.
        """
        from app.services.member_management import MemberManagement

        async with uow:
            has_permission = await MemberManagement.check_is_user_have_permission(
                uow, current_user_id, answer.company_id
            )
            if not has_permission:
                raise UnAuthorizedException()

            updated_answer = await uow.answer.edit_one(answer_id, answer.dict())
            return AnswerBase(**updated_answer.__dict__)

    @staticmethod
    async def get_answer_by_id(
        uow: UnitOfWork, answer_id: int, current_user_id: int
    ) -> AnswerBase:
        """
        Retrieve an answer by its ID.

        Args:
            uow (UnitOfWork): The unit of work object for database transactions.
            answer_id (int): The ID of the answer to retrieve.
            current_user_id (int): The ID of the user requesting the answer.

        Returns:
            AnswerBase: The retrieved answer.

        Raises:
            NotFoundException: If the answer is not found.
            UnAuthorizedException: If the user does not have permission.
        """
        from app.services.member_management import MemberManagement

        async with uow:
            answer = await uow.answer.find_one(id=answer_id)
            if not answer:
                raise NotFoundException()

            has_permission = await MemberManagement.check_is_user_have_permission(
                uow, current_user_id, answer.company_id
            )
            if not has_permission:
                raise UnAuthorizedException()

            return AnswerBase(**answer.__dict__)

    @staticmethod
    async def get_answers(
        uow: UnitOfWork,
        company_id: int,
        current_user_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> AnswersListResponse:
        """
        Retrieve a list of answers for a given company.

        Args:
            uow (UnitOfWork): The unit of work object for database transactions.
            company_id (int): The ID of the company whose answers are being retrieved.
            current_user_id (int): The ID of the user requesting the answers.
            skip (int): Number of answers to skip (default 0).
            limit (int): Maximum number of answers to return (default 10).

        Returns:
            AnswersListResponse: The list of answers with total count.

        Raises:
            UnAuthorizedException: If the user does not have permission.
        """
        from app.services.member_management import MemberManagement

        async with uow:
            has_permission = await MemberManagement.check_is_user_have_permission(
                uow, current_user_id, company_id
            )
            if not has_permission:
                raise UnAuthorizedException()

            answers = await uow.answer.find_all(skip=skip, limit=limit)
            answer_list = AnswersListResponse(
                answers=[AnswerBase(**answer.__dict__) for answer in answers],
                total=len(answers),
            )
            return answer_list

    @staticmethod
    async def delete_answer(
        uow: UnitOfWork, answer_id: int, current_user_id: int
    ) -> AnswerBase:
        """
        Delete an answer by its ID.

        Args:
            uow (UnitOfWork): The unit of work object for database transactions.
            answer_id (int): The ID of the answer to delete.
            current_user_id (int): The ID of the user performing the deletion.

        Returns:
            AnswerBase: The deleted answer.

        Raises:
            NotFoundException: If the answer is not found.
            UnAuthorizedException: If the user does not have permission.
        """
        from app.services.member_management import MemberManagement

        async with uow:
            answer_to_delete = await uow.answer.find_one(id=answer_id)
            if not answer_to_delete:
                raise NotFoundException()

            has_permission = await MemberManagement.check_is_user_have_permission(
                uow, current_user_id, answer_to_delete.company_id
            )
            if not has_permission:
                raise UnAuthorizedException()

            deleted_answer = await uow.answer.delete_one(answer_id)
            return AnswerBase(**deleted_answer.__dict__)
