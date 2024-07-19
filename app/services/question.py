from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException, FetchingException
from app.schemas.answer import AnswerBase
from app.schemas.question import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionBase,
    QuestionsListResponse,
    QuestionResponseForList,
)
from app.services.member import MemberService
from app.uow.unitofwork import UnitOfWork


class QuestionService:
    @staticmethod
    async def create_question(
        uow: UnitOfWork, question: QuestionCreate, current_user_id: int
    ) -> QuestionBase:
        async with uow:
            has_permission = await MemberService.check_is_user_have_permission(
                uow, current_user_id, question.company_id
            )
            if not has_permission:
                raise UnAuthorizedException()

            new_question = await uow.question.add_one(
                question.dict(exclude={"answers", "id"})
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
                    raise NotFoundException()

            return QuestionBase(**new_question.__dict__)

    @staticmethod
    async def update_question(
        uow: UnitOfWork,
        question_id: int,
        question: QuestionUpdate,
        current_user_id: int,
    ) -> QuestionBase:
        async with uow:
            question_to_update = await uow.question.find_one(id=question_id)
            if not question_to_update:
                raise NotFoundException()

            has_permission = await MemberService.check_is_user_have_permission(
                uow, current_user_id, question_to_update.company_id
            )
            if not has_permission:
                raise UnAuthorizedException()

            updated_question = await uow.question.edit_one(question_id, question.dict())
            return QuestionBase(**updated_question.__dict__)

    @staticmethod
    async def get_question_by_id(
        uow: UnitOfWork, question_id: int, current_user_id: int
    ) -> QuestionResponse:
        async with uow:

            answers = await uow.answer.find_all_by_question_id(question_id=question_id)

            if len(answers) < 2 or len(answers) > 4:
                raise FetchingException()

            question = await uow.question.find_one(id=question_id)
            if not question:
                raise NotFoundException()

            has_permission = await MemberService.check_is_user_member_or_higher(
                uow, current_user_id, question.company_id
            )

            if not has_permission:
                raise UnAuthorizedException()

            answers = await uow.answer.find_all_by_question_id(question_id=question_id)
            question_data = {
                "id": question_id,
                "title": question.title,
                "answers": [AnswerBase(**answer.__dict__) for answer in answers],
            }

            return QuestionResponse(**question_data)

    @staticmethod
    async def get_questions(
        uow: UnitOfWork,
        company_id: int,
        current_user_id,
        skip: int = 0,
        limit: int = 10,
    ) -> QuestionsListResponse:
        async with uow:
            has_permission = await MemberService.check_is_user_have_permission(
                uow, current_user_id, company_id
            )
            if not has_permission:
                raise UnAuthorizedException()

            questions = await uow.question.find_all(skip=skip, limit=limit)

            question_list = QuestionsListResponse(
                questions=[
                    QuestionResponseForList(**question.__dict__)
                    for question in questions
                ],
                total=len(questions),
            )

            return question_list

    @staticmethod
    async def delete_question(
        uow: UnitOfWork, question_id: int, current_user_id: int
    ) -> QuestionBase:
        async with uow:
            question_to_delete = await uow.question.find_one(id=question_id)
            if not question_to_delete:
                raise NotFoundException()

            has_permission = await MemberService.check_is_user_have_permission(
                uow, current_user_id, question_to_delete.company_id
            )
            if not has_permission:
                raise UnAuthorizedException()

            answers = await uow.answer.find_all_by_question_id(question_id=question_id)

            for answer in answers:
                await uow.answer.edit_one(
                    answer.id, {"question_id": None, "company_id": None}
                )

            deleted_question = await uow.question.delete_one(question_id)
            return QuestionBase(**deleted_question.__dict__)
