import pandas as pd
from fastapi import UploadFile
from app.core.logger import logger
from app.schemas.answer import AnswerCreate
from app.schemas.question import QuestionCreate
from app.schemas.quiz import QuizCreate
from app.services.answer import AnswerService
from app.services.question import QuestionService
from app.services.quiz import QuizService
from app.uow.unitofwork import UnitOfWork


class DataImportService:
    @staticmethod
    async def import_data(file: UploadFile, uow: UnitOfWork, current_user_id: int):
        """
        Parses the Excel file and processes answers, questions, and quizzes.

        Args:
            file (UploadFile): The Excel file to be parsed.
            uow (UnitOfWork): The unit of work for database operations.
            current_user_id (int): The ID of the current user.

        Raises:
            Exception: If there is an error during the import process.
        """
        try:
            # Parse Excel file
            sheets = DataImportService.parse_excel(file)

            # Parse updates
            updates_mapping = DataImportService.parse_updates(sheets["Updates"])
            logger.info(f"{updates_mapping}")

            await DataImportService.process_answers(
                sheets["Answers"], uow, current_user_id, updates_mapping
            )
            await DataImportService.process_questions(
                sheets["Questions"], uow, current_user_id, updates_mapping
            )
            await DataImportService.process_quizzes(
                sheets["Quizzes"], uow, current_user_id, updates_mapping
            )

        except Exception as e:
            logger.error(f"Error parsing Excel file: {e}")
            raise

    @staticmethod
    def parse_excel(file: UploadFile) -> dict:
        """
        Reads the required sheets from the Excel file.

        Args:
            file (UploadFile): The Excel file to be read.

        Returns:
            dict: A dictionary containing the DataFrames for the required sheets.

        Raises:
            ValueError: If a required sheet is missing from the Excel file.
        """
        excel_file = pd.ExcelFile(file.file, engine="openpyxl")
        sheet_names = excel_file.sheet_names
        logger.info(f"Available sheet names: {sheet_names}")

        required_sheets = ["Quizzes", "Questions", "Answers", "Updates"]
        for sheet in required_sheets:
            if sheet not in sheet_names:
                raise ValueError(f"Missing required sheet: {sheet}")

        sheets = {
            sheet: pd.read_excel(file.file, sheet_name=sheet)
            for sheet in required_sheets
        }
        return sheets

    @staticmethod
    def parse_updates(df_updates: pd.DataFrame) -> dict:
        """
        Extracts updates mapping from the updates DataFrame.

        Args:
            df_updates (pd.DataFrame): The DataFrame containing the updates.

        Returns:
            dict: A dictionary mapping old titles to new titles.
        """
        updates_mapping = {
            row["Unique Title"]: row["New Title"]
            for index, row in df_updates.iterrows()
        }
        return updates_mapping

    @staticmethod
    async def process_answers(
        df_answers: pd.DataFrame,
        uow: UnitOfWork,
        current_user_id: int,
        updates_mapping: dict,
    ):
        """
        Processes the answers DataFrame and creates or updates answers.

        Args:
            df_answers (pd.DataFrame): The DataFrame containing the answers.
            uow (UnitOfWork): The unit of work for database operations.
            current_user_id (int): The ID of the current user.
            updates_mapping (dict): A dictionary mapping old titles to new titles.
        """
        async with uow:
            for index, row in df_answers.iterrows():
                await DataImportService.handle_answer_row(
                    row, uow, current_user_id, updates_mapping
                )

    @staticmethod
    async def handle_answer_row(
        row: pd.Series, uow: UnitOfWork, current_user_id: int, updates_mapping: dict
    ):
        """
        Handles the creation or update of a single answer.

        Args:
            row (pd.Series): The row of the DataFrame containing the answer data.
            uow (UnitOfWork): The unit of work for database operations.
            current_user_id (int): The ID of the current user.
            updates_mapping (dict): A dictionary mapping old titles to new titles.
        """
        answer_text = str(row["Text"])
        try:
            existing_answer = await uow.answer.find_one(text=answer_text)
            if existing_answer:
                if answer_text in updates_mapping:
                    new_text = updates_mapping[answer_text]
                    await uow.answer.edit_one(
                        id=existing_answer.id, data={"text": new_text}
                    )
                    logger.info(f"Updated answer with ID {existing_answer.id}")
                logger.info(
                    f"Answer with title '{answer_text}' already exists, skipping."
                )
                return

            answer_data = AnswerCreate(
                text=answer_text,
                is_correct=bool(row["Is Correct"]),
                company_id=int(row["Company ID"]),
            )
            await AnswerService.create_answer(uow, answer_data, current_user_id)

        except Exception as e:
            logger.error(f"Error creating answer with text '{answer_text}': {e}")

    @staticmethod
    async def process_questions(
        df_questions: pd.DataFrame,
        uow: UnitOfWork,
        current_user_id: int,
        updates_mapping: dict,
    ):
        """
        Processes the questions DataFrame and creates or updates questions.

        Args:
            df_questions (pd.DataFrame): The DataFrame containing the questions.
            uow (UnitOfWork): The unit of work for database operations.
            current_user_id (int): The ID of the current user.
            updates_mapping (dict): A dictionary mapping old titles to new titles.
        """
        async with uow:
            for index, row in df_questions.iterrows():
                await DataImportService.handle_question_row(
                    row, uow, current_user_id, updates_mapping
                )

    @staticmethod
    async def handle_question_row(
        row: pd.Series, uow: UnitOfWork, current_user_id: int, updates_mapping: dict
    ):
        """
        Handles the creation or update of a single question.

        Args:
            row (pd.Series): The row of the DataFrame containing the question data.
            uow (UnitOfWork): The unit of work for database operations.
            current_user_id (int): The ID of the current user.
            updates_mapping (dict): A dictionary mapping old titles to new titles.
        """
        question_title = str(row["Title"])
        try:
            existing_question = await uow.question.find_one(title=question_title)
            if existing_question:
                if question_title in updates_mapping:
                    new_title = updates_mapping[question_title]
                    await uow.question.edit_one(
                        id=existing_question.id, data={"title": new_title}
                    )
                    logger.info(f"Updated question with ID {existing_question.id}")
                logger.info(
                    f"Question with title '{question_title}' already exists, skipping."
                )
                return

            answer_ids = await DataImportService.get_answer_ids(row["Answers"], uow)
            question_data = QuestionCreate(
                title=question_title,
                answers=answer_ids,
                company_id=int(row["Company ID"]),
            )
            await QuestionService.create_question(uow, question_data, current_user_id)

        except Exception as e:
            logger.error(f"Error creating question with title '{question_title}': {e}")

    @staticmethod
    async def get_answer_ids(answer_texts: str, uow: UnitOfWork) -> set:
        """
        Retrieves the IDs of answers from their texts.

        Args:
            answer_texts (str): A comma-separated string of answer texts.
            uow (UnitOfWork): The unit of work for database operations.

        Returns:
            set: A set of answer IDs.
        """
        answer_ids = set()
        for text in answer_texts.split(", "):
            existing_answer = await uow.answer.find_one(text=text)
            if existing_answer:
                answer_ids.add(existing_answer.id)
            else:
                logger.info(f"Answer with text '{text}' not found, skipping.")
        return answer_ids

    @staticmethod
    async def process_quizzes(
        df_quizzes: pd.DataFrame,
        uow: UnitOfWork,
        current_user_id: int,
        updates_mapping: dict,
    ):
        """
        Processes the quizzes DataFrame and creates or updates quizzes.

        Args:
            df_quizzes (pd.DataFrame): The DataFrame containing the quizzes.
            uow (UnitOfWork): The unit of work for database operations.
            current_user_id (int): The ID of the current user.
            updates_mapping (dict): A dictionary mapping old titles to new titles.
        """
        async with uow:
            for index, row in df_quizzes.iterrows():
                await DataImportService.handle_quiz_row(
                    row, uow, current_user_id, updates_mapping
                )

    @staticmethod
    async def handle_quiz_row(
        row: pd.Series, uow: UnitOfWork, current_user_id: int, updates_mapping: dict
    ):
        """
        Handles the creation or update of a single quiz.

        Args:
            row (pd.Series): The row of the DataFrame containing the quiz data.
            uow (UnitOfWork): The unit of work for database operations.
            current_user_id (int): The ID of the current user.
            updates_mapping (dict): A dictionary mapping old titles to new titles.
        """
        quiz_title = str(row["Title"])
        try:
            question_ids = await DataImportService.get_question_ids(
                row["Questions"], uow
            )
            existing_quiz = await uow.quiz.find_one(title=quiz_title)
            if not existing_quiz:
                quiz_data = QuizCreate(
                    title=quiz_title,
                    description=str(row["Description"]),
                    frequency=(
                        int(row["Frequency"]) if not pd.isna(row["Frequency"]) else 0
                    ),
                    company_id=int(row["Company ID"]),
                    questions=question_ids,
                )
                await QuizService.create_quiz(uow, quiz_data, current_user_id)
            else:
                if quiz_title in updates_mapping:
                    new_title = updates_mapping[quiz_title]
                    await uow.quiz.edit_one(
                        id=existing_quiz.id, data={"title": new_title}
                    )
                    logger.info(f"Updated quiz with ID {existing_quiz.id}")

        except Exception as e:
            logger.error(
                f"Error creating or updating quiz with title '{quiz_title}': {e}"
            )

    @staticmethod
    async def get_question_ids(question_titles: str, uow: UnitOfWork) -> list:
        """
        Retrieves the IDs of questions from their titles.

        Args:
            question_titles (str): A comma-separated string of question titles.
            uow (UnitOfWork): The unit of work for database operations.

        Returns:
            list: A list of question IDs.
        """
        question_ids = []
        for title in question_titles.split(", "):
            existing_question = await uow.question.find_one(title=title)
            if existing_question:
                question_ids.append(existing_question.id)
            else:
                logger.info(f"Question with title '{title}' not found, skipping.")
        return question_ids
