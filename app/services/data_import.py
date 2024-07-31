import pandas as pd
from fastapi import UploadFile
from app.core.logger import logger
from app.schemas.answer import AnswerCreate
from app.schemas.question import QuestionCreate
from app.schemas.quiz import QuizCreate
from app.services.member_management import MemberManagement
from app.uow.unitofwork import UnitOfWork
from app.services.answer import AnswerService
from app.services.question import QuestionService
from app.services.quiz import QuizService


class DataImportService:
    @staticmethod
    async def parse_excel(file: UploadFile, uow: UnitOfWork, current_user_id: int):
        try:
            # List available sheet names
            excel_file = pd.ExcelFile(file.file, engine="openpyxl")
            sheet_names = excel_file.sheet_names
            logger.info(f"Available sheet names: {sheet_names}")

            # Check if necessary sheets are present
            required_sheets = ["Quizzes", "Questions", "Answers"]
            for sheet in required_sheets:
                if sheet not in sheet_names:
                    raise ValueError(f"Missing required sheet: {sheet}")

            # Read the required sheets
            df_quizzes = pd.read_excel(file.file, sheet_name="Quizzes")
            logger.info(f"Quizzes DataFrame: {df_quizzes.head()}")

            df_questions = pd.read_excel(file.file, sheet_name="Questions")
            logger.info(f"Questions DataFrame: {df_questions.head()}")

            df_answers = pd.read_excel(file.file, sheet_name="Answers")
            logger.info(f"Answers DataFrame: {df_answers.head()}")

            # Create answers
            answers_mapping = {}
            for index, row in df_answers.iterrows():
                answer_data = AnswerCreate(
                    text=str(row["Text"]),
                    is_correct=bool(row["Is Correct"]),
                    company_id=int(row["Company ID"]),
                )
                answer = await AnswerService.create_answer(
                    uow, answer_data, current_user_id
                )
                answers_mapping[row["Answer ID"]] = answer.id

            # Create questions
            questions_mapping = {}
            for index, row in df_questions.iterrows():
                question_data = QuestionCreate(
                    title=str(row["Title"]),
                    company_id=int(row["Company ID"]),
                    answers={
                        answers_mapping[int(aid)] for aid in row["Answers"].split(",")
                    },
                )
                question = await QuestionService.create_question(
                    uow, question_data, current_user_id
                )
                questions_mapping[row["Question ID"]] = question.id

            # Create quizzes
            for index, row in df_quizzes.iterrows():
                quiz_data = QuizCreate(
                    title=str(row["Title"]),
                    description=str(row["Description"]),
                    frequency=int(row["Frequency"]),
                    company_id=int(row["Company ID"]),
                    questions=[
                        questions_mapping[int(qid)]
                        for qid in row["Questions"].split(",")
                    ],
                )
                await QuizService.create_quiz(uow, quiz_data, current_user_id)

        except Exception as e:
            logger.error(f"Error parsing Excel file: {e}")
            raise
