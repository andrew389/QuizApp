from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException
from app.schemas.answer import AnswerUpdate, AnswerCreate, AnswerBase
from app.services.member import MemberService
from app.uow.unitofwork import UnitOfWork, IUnitOfWork


class AnswerService:
    @staticmethod
    async def create_answer(
        uow: UnitOfWork, answer: AnswerCreate, current_user_id: int
    ):
        async with uow:
            has_permission = await MemberService.check_is_user_have_permission(
                uow, current_user_id, answer.company_id
            )
            if not has_permission:
                raise UnAuthorizedException()
            new_answer = await uow.answer.add_one(answer.dict(exclude={"id"}))
            return AnswerBase(**new_answer.__dict__)

    @staticmethod
    async def validate_answer_update(
        uow: IUnitOfWork, answer_id: int, answer_update: AnswerUpdate
    ) -> AnswerUpdate:
        current_answer = await uow.answer.find_one(id=answer_id)
        if not current_answer:
            raise NotFoundException()

        answer_data = answer_update.model_dump()
        fields_to_check = answer_data.keys()
        default_values = ["string"]

        for field_name in fields_to_check:
            field_value = answer_data[field_name]
            if field_value in [None, *default_values]:
                setattr(answer_update, field_name, getattr(current_answer, field_name))

        return answer_update

    @staticmethod
    async def update_answer(
        uow: UnitOfWork, answer_id: int, answer: AnswerUpdate, current_user_id: int
    ):
        async with uow:
            has_permission = await MemberService.check_is_user_have_permission(
                uow, current_user_id, answer.company_id
            )
            if not has_permission:
                raise UnAuthorizedException()

            answer_update = await AnswerService.validate_answer_update(
                uow, answer_id, answer
            )
            updated_answer = await uow.answer.edit_one(answer_id, answer_update.dict())
            return AnswerBase(**updated_answer.__dict__)

    @staticmethod
    async def get_answer_by_id(uow: UnitOfWork, answer_id: int, current_user_id):
        async with uow:
            answer = await uow.answer.find_one(id=answer_id)
            if not answer:
                raise NotFoundException()

            has_permission = await MemberService.check_is_user_member_or_higher(
                uow, current_user_id, answer.company_id
            )

            if not has_permission:
                raise UnAuthorizedException()

            return AnswerBase(**answer.__dict__)

    @staticmethod
    async def delete_answer(uow: UnitOfWork, answer_id: int, current_user_id: int):
        async with uow:
            answer_to_delete = await uow.answer.find_one(id=answer_id)
            if not answer_to_delete:
                raise NotFoundException()

            has_permission = await MemberService.check_is_user_have_permission(
                uow, current_user_id, answer_to_delete.company_id
            )
            if not has_permission:
                raise UnAuthorizedException()

            deleted_answer = await uow.answer.delete_one(answer_id)
            return AnswerBase(**deleted_answer.__dict__)
