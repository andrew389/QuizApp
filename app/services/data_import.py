import pandas as pd
from fastapi import UploadFile
from app.schemas.quiz import QuizCreate
from app.services.member_management import MemberManagement
from app.uow.unitofwork import UnitOfWork


class DataImportService:
    @staticmethod
    async def parse_excel(file: UploadFile) -> list:
        df_quizzes = pd.read_excel(file.file, sheet_name="Quizzes")
        df_questions = pd.read_excel(file.file, sheet_name="Questions")
        df_answers = pd.read_excel(file.file, sheet_name="Answers")

        quizzes = []

        for _, quiz_row in df_quizzes.iterrows():
            quiz = {
                "title": quiz_row["Title"],
                "description": quiz_row["Description"],
                "frequency": quiz_row["Frequency"],
                "company_id": quiz_row["Company ID"],
                "questions": [],
            }

            quiz_questions = df_questions[
                df_questions["Quiz ID"] == quiz_row["Quiz ID"]
            ]

            for _, question_row in quiz_questions.iterrows():
                question = {"title": question_row["Title"], "answers": []}

                question_answers = df_answers[
                    df_answers["Question ID"] == question_row["Question ID"]
                ]

                for _, answer_row in question_answers.iterrows():
                    answer = {
                        "text": answer_row["Text"],
                        "is_correct": answer_row["Is Correct"],
                        "company_id": answer_row["Company ID"],
                    }
                    question["answers"].append(answer)

                quiz["questions"].append(question)

            quizzes.append(quiz)

        return quizzes

    @staticmethod
    async def validate_quiz_data(quiz_data: dict) -> QuizCreate:
        return QuizCreate(**quiz_data)

    @staticmethod
    async def process_quiz_data(uow: UnitOfWork, quiz_data: QuizCreate):
        async with uow:
            existing_quiz = await uow.quiz.get_by_title(quiz_data.title)

            if existing_quiz:
                await uow.quiz.update(existing_quiz, quiz_data.dict())
            else:
                await uow.quiz.create(quiz_data.dict())

            await uow.commit()

    @staticmethod
    async def import_quizzes(uow: UnitOfWork, user_id: int, file: UploadFile):
        async with uow:
            member = await uow.member.find_one(user_id=user_id)

        await MemberManagement.check_is_user_have_permission(
            uow, user_id, member.company_id
        )

        quizzes_data = await DataImportService.parse_excel(file)

        for quiz_data in quizzes_data:
            valid_quiz = await DataImportService.validate_quiz_data(quiz_data)
            if valid_quiz:
                await DataImportService.process_quiz_data(uow, valid_quiz)
