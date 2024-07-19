from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException
from app.schemas.question import QuestionBase, QuestionResponse
from app.schemas.quiz import QuizCreate, QuizResponse, QuizBase, QuizUpdate
from app.services.member import MemberService
from app.services.question import QuestionService
from app.uow.unitofwork import UnitOfWork, IUnitOfWork


class QuizService:
    @staticmethod
    async def create_quiz(
        uow: UnitOfWork, quiz: QuizCreate, current_user_id: int
    ) -> QuizBase:
        async with uow:
            has_permission = await MemberService.check_is_user_have_permission(
                uow, current_user_id, quiz.company_id
            )
            if not has_permission:
                raise UnAuthorizedException()

            new_quiz = await uow.quiz.add_one(quiz.dict(exclude={"questions", "id"}))

            for question_id in quiz.questions:
                existing_question = await uow.question.find_one(
                    id=question_id, quiz_id=None
                )
                if existing_question:
                    await uow.question.edit_one(question_id, {"quiz_id": new_quiz.id})
                else:
                    raise NotFoundException()

            return QuizBase(**new_quiz.__dict__)

    @staticmethod
    async def validate_quiz_update(
        uow: IUnitOfWork, quiz_id: int, quiz_update: QuizUpdate
    ) -> QuizUpdate:
        current_quiz = await uow.quiz.find_one(id=quiz_id)
        if not current_quiz:
            raise NotFoundException()

        quiz_data = quiz_update.model_dump()
        fields_to_check = quiz_data.keys()
        default_values = ["string"]

        for field_name in fields_to_check:
            field_value = quiz_data[field_name]
            if field_value in [None, *default_values]:
                setattr(quiz_update, field_name, getattr(current_quiz, field_name))
            if field_name == "questions" and not field_value:
                current_questions = await uow.question.find_all_by_quiz_id(
                    quiz_id=quiz_id
                )
                setattr(
                    quiz_update,
                    "questions",
                    [question.id for question in current_questions],
                )

        return quiz_update

    @staticmethod
    async def update_quiz(
        uow: UnitOfWork, quiz_id: int, quiz: QuizUpdate, current_user_id: int
    ) -> QuizBase:
        async with uow:
            quiz_update = await QuizService.validate_quiz_update(uow, quiz_id, quiz)
            quiz_to_update = await uow.quiz.find_one(id=quiz_id)
            if not quiz_to_update:
                raise NotFoundException()

            has_permission = await MemberService.check_is_user_have_permission(
                uow, current_user_id, quiz_to_update.company_id
            )
            if not has_permission:
                raise UnAuthorizedException()

            updated_quiz = await uow.quiz.edit_one(quiz_id, quiz_update.dict())
            return QuizBase(**updated_quiz.__dict__)

    @staticmethod
    async def get_quiz_by_id(
        uow: UnitOfWork, quiz_id: int, current_user_id: int
    ) -> QuizResponse:
        async with uow:
            quiz = await uow.quiz.find_one(id=quiz_id)
            if not quiz:
                raise NotFoundException()

            has_permission = await MemberService.check_is_user_member_or_higher(
                uow, current_user_id, quiz.company_id
            )

            if not has_permission:
                raise UnAuthorizedException()

            questions = await uow.question.find_all_by_quiz_id(quiz_id=quiz_id)
            quiz_data = {
                "title": quiz.title,
                "description": quiz.description,
                "frequency": quiz.frequency,
                "questions": [],
            }

            for question in questions:
                question_data = await QuestionService.get_question_by_id(
                    uow, question.id, current_user_id
                )

                quiz_data["questions"].append(
                    QuestionResponse(**question_data.__dict__)
                )

            return QuizResponse(**quiz_data)

    @staticmethod
    async def delete_quiz(
        uow: UnitOfWork, quiz_id: int, current_user_id: int
    ) -> QuizBase:
        async with uow:
            quiz_to_delete = await uow.quiz.find_one(id=quiz_id)
            if not quiz_to_delete:
                raise NotFoundException()

            has_permission = await MemberService.check_is_user_have_permission(
                uow, current_user_id, quiz_to_delete.company_id
            )
            if not has_permission:
                raise UnAuthorizedException()

            deleted_quiz = await uow.quiz.delete_one(quiz_id)
            return QuizBase(**deleted_quiz.__dict__)
