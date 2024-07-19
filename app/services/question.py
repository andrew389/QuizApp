from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException
from app.schemas.answer import AnswerBase
from app.schemas.question import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionBase,
)
from app.services.member import MemberService
from app.uow.unitofwork import UnitOfWork, IUnitOfWork


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
    async def validate_question_update(
        uow: IUnitOfWork, question_id: int, question_update: QuestionUpdate
    ) -> QuestionUpdate:
        current_question = await uow.question.find_one(id=question_id)
        if not current_question:
            raise NotFoundException()

        question_data = question_update.model_dump()
        fields_to_check = question_data.keys()
        default_values = ["string"]

        for field_name in fields_to_check:
            field_value = question_data[field_name]
            if field_value in [None, *default_values]:
                setattr(
                    question_update, field_name, getattr(current_question, field_name)
                )
            if field_name == "answers" and (
                field_value is None or len(field_value) == 0
            ):
                current_answers = await uow.answer.find_all_by_question_id(
                    question_id=question_id
                )
                setattr(
                    question_update,
                    "answers",
                    [answer.id for answer in current_answers],
                )

        return question_update

    @staticmethod
    async def update_question(
        uow: UnitOfWork,
        question_id: int,
        question: QuestionUpdate,
        current_user_id: int,
    ) -> QuestionBase:
        async with uow:
            question_update = await QuestionService.validate_question_update(
                uow, question_id, question
            )
            question_to_update = await uow.question.find_one(id=question_id)
            if not question_to_update:
                raise NotFoundException()

            has_permission = await MemberService.check_is_user_have_permission(
                uow, current_user_id, question_to_update.company_id
            )
            if not has_permission:
                raise UnAuthorizedException()

            updated_question = await uow.question.edit_one(
                question_id, question_update.dict()
            )
            return QuestionBase(**updated_question.__dict__)

    @staticmethod
    async def get_question_by_id(
        uow: UnitOfWork, question_id: int, current_user_id: int
    ) -> QuestionResponse:
        async with uow:
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

            deleted_question = await uow.question.delete_one(question_id)
            return QuestionBase(**deleted_question.__dict__)
