import pandas as pd
from fastapi import UploadFile
from app.core.logger import logger
from app.schemas.answer import AnswerCreate, AnswerUpdate
from app.schemas.question import QuestionCreate, QuestionUpdate
from app.schemas.quiz import QuizCreate, QuizUpdate
from app.services.answer import AnswerService
from app.services.question import QuestionService
from app.services.quiz import QuizService
from app.uow.unitofwork import UnitOfWork


class DataImportService:
    """
    Service for importing quiz data from an Excel file into the database.

    This service provides methods to parse an Excel file and process its contents to
    create, update, or delete records in the database for quizzes, questions, and answers.
    It ensures that the data in the database is synchronized with the data provided in the Excel file.

    Methods:
        - import_data: Main entry point for importing data from an Excel file.
        - parse_excel: Parses the Excel file and extracts required sheets.
        - process_sheets: Processes the parsed sheets to handle answers, questions, and quizzes.
        - process_answers: Processes the answers sheet to create, update, or delete answer records.
        - delete_answers: Deletes answers from the database based on the parsed data.
        - create_or_update_answer: Creates or updates an answer in the database.
        - process_questions: Processes the questions sheet to create, update, or delete question records.
        - delete_questions: Deletes questions from the database based on the parsed data.
        - create_or_update_question: Creates or updates a question in the database.
        - process_quizzes: Processes the quizzes sheet to create, update, or delete quiz records.
        - delete_quizzes: Deletes quizzes from the database based on the parsed data.
        - create_or_update_quiz: Creates or updates a quiz in the database.
        - get_answer_ids: Retrieves IDs of answers based on their text.
        - get_question_ids: Retrieves IDs of questions based on their titles.
    """

    @staticmethod
    async def import_data(file: UploadFile, uow: UnitOfWork, current_user_id: int):
        """
        Imports data from an Excel file and processes it to update the database.

        Args:
            file (UploadFile): The uploaded Excel file containing quiz data.
            uow (UnitOfWork): An instance of UnitOfWork for database operations.
            current_user_id (int): The ID of the current user performing the import.

        Raises:
            Exception: If there is an error during the parsing or processing of the Excel file.
        """
        try:
            sheets = DataImportService.parse_excel(file)
            await DataImportService.process_sheets(sheets, uow, current_user_id)
        except Exception as e:
            logger.error(f"Error parsing Excel file: {e}")
            raise

    @staticmethod
    def parse_excel(file: UploadFile) -> dict:
        """
        Parses the provided Excel file and extracts required sheets.

        Args:
            file (UploadFile): The uploaded Excel file containing quiz data.

        Returns:
            dict: A dictionary with sheet names as keys and their corresponding DataFrames as values.

        Raises:
            ValueError: If any of the required sheets are missing.
        """
        excel_file = pd.ExcelFile(file.file, engine="openpyxl")
        sheet_names = excel_file.sheet_names
        logger.info(f"Available sheet names: {sheet_names}")

        required_sheets = ["Quizzes", "Questions", "Answers"]
        for sheet in required_sheets:
            if sheet not in sheet_names:
                raise ValueError(f"Missing required sheet: {sheet}")

        sheets = {
            sheet: pd.read_excel(file.file, sheet_name=sheet)
            for sheet in required_sheets
        }
        return sheets

    @staticmethod
    async def process_sheets(sheets: dict, uow: UnitOfWork, current_user_id: int):
        """
        Processes the parsed sheets to handle answers, questions, and quizzes.

        Args:
            sheets (dict): A dictionary with sheet names as keys and their corresponding DataFrames as values.
            uow (UnitOfWork): An instance of UnitOfWork for database operations.
            current_user_id (int): The ID of the current user performing the import.
        """
        await DataImportService.process_answers(sheets["Answers"], uow, current_user_id)
        await DataImportService.process_questions(
            sheets["Questions"], uow, current_user_id
        )
        await DataImportService.process_quizzes(sheets["Quizzes"], uow, current_user_id)

    @staticmethod
    async def process_answers(
        df_answers: pd.DataFrame, uow: UnitOfWork, current_user_id: int
    ):
        """
        Processes the answers sheet to create, update, or delete answer records.

        Args:
            df_answers (pd.DataFrame): DataFrame containing answers data.
            uow (UnitOfWork): An instance of UnitOfWork for database operations.
            current_user_id (int): The ID of the current user performing the import.
        """
        async with uow:
            existing_answers = {a.text: a.id for a in await uow.answer.find_all()}
            new_answers = set(df_answers["Text"].dropna().astype(str))

            to_delete = set(existing_answers.keys()) - new_answers

            if to_delete:
                await DataImportService.delete_answers(
                    to_delete, existing_answers, uow, current_user_id
                )
            else:
                for index, row in df_answers.iterrows():
                    await DataImportService.create_or_update_answer(
                        row, uow, current_user_id
                    )

    @staticmethod
    async def delete_answers(
        to_delete: set, existing_answers: dict, uow: UnitOfWork, current_user_id: int
    ):
        """
        Deletes answers from the database based on the parsed data.

        Args:
            to_delete (set): Set of answer texts to be deleted.
            existing_answers (dict): Dictionary of existing answers with their texts as keys and IDs as values.
            uow (UnitOfWork): An instance of UnitOfWork for database operations.
            current_user_id (int): The ID of the current user performing the import.
        """
        for text in to_delete:
            await AnswerService.delete_answer(
                uow, existing_answers[text], current_user_id
            )
            logger.info(f"Deleted answer with text '{text}'")

    @staticmethod
    async def create_or_update_answer(
        row: pd.Series, uow: UnitOfWork, current_user_id: int
    ):
        """
        Creates or updates an answer in the database.

        Args:
            row (pd.Series): Series containing data for a single answer.
            uow (UnitOfWork): An instance of UnitOfWork for database operations.
            current_user_id (int): The ID of the current user performing the import.
        """
        async with uow:
            answer_text = str(row["Text"])
            is_correct = bool(row["Is Correct"])
            company_id = int(row["Company ID"])

            try:
                existing_answer = await uow.answer.find_one(text=answer_text)
                if existing_answer:
                    if (
                        existing_answer.is_correct == is_correct
                        and existing_answer.company_id == company_id
                    ):
                        logger.info(
                            f"Answer with text '{answer_text}' is up-to-date, skipping."
                        )
                        return

                    logger.info(f"Updating existing answer with text '{answer_text}'.")
                    updated_answer_data = AnswerUpdate(
                        text=answer_text, company_id=company_id, is_correct=is_correct
                    )
                    await AnswerService.update_answer(
                        uow, existing_answer.id, updated_answer_data, current_user_id
                    )

                else:
                    answer_data = AnswerCreate(
                        text=answer_text, is_correct=is_correct, company_id=company_id
                    )
                    await AnswerService.create_answer(uow, answer_data, current_user_id)
                    logger.info(f"Created new answer with text '{answer_text}'.")

            except Exception as e:
                logger.error(f"Error handling answer with text '{answer_text}': {e}")

    @staticmethod
    async def process_questions(
        df_questions: pd.DataFrame, uow: UnitOfWork, current_user_id: int
    ):
        """
        Processes the questions sheet to create, update, or delete question records.

        Args:
            df_questions (pd.DataFrame): DataFrame containing questions data.
            uow (UnitOfWork): An instance of UnitOfWork for database operations.
            current_user_id (int): The ID of the current user performing the import.
        """
        async with uow:
            existing_questions = {q.title: q.id for q in await uow.question.find_all()}
            new_questions = set(df_questions["Title"].dropna().astype(str))

            to_delete = set(existing_questions.keys()) - new_questions

            if to_delete:
                await DataImportService.delete_questions(
                    to_delete, existing_questions, uow, current_user_id
                )
            else:
                for index, row in df_questions.iterrows():
                    await DataImportService.create_or_update_question(
                        row, uow, current_user_id
                    )

    @staticmethod
    async def delete_questions(
        to_delete: set, existing_questions: dict, uow: UnitOfWork, current_user_id: int
    ):
        """
        Deletes questions from the database based on the parsed data.

        Args:
            to_delete (set): Set of question titles to be deleted.
            existing_questions (dict): Dictionary of existing questions with their titles as keys and IDs as values.
            uow (UnitOfWork): An instance of UnitOfWork for database operations.
            current_user_id (int): The ID of the current user performing the import.
        """
        for title in to_delete:
            await QuestionService.delete_question(
                uow, existing_questions[title], current_user_id
            )
            logger.info(f"Deleted question with title '{title}'")

    @staticmethod
    async def create_or_update_question(
        row: pd.Series, uow: UnitOfWork, current_user_id: int
    ):
        """
        Creates or updates a question in the database.

        Args:
            row (pd.Series): Series containing data for a single question.
            uow (UnitOfWork): An instance of UnitOfWork for database operations.
            current_user_id (int): The ID of the current user performing the import.
        """
        question_title = str(row["Title"])
        company_id = int(row["Company ID"])
        async with uow:
            try:
                existing_question = await uow.question.find_one(title=question_title)
                answer_ids = await DataImportService.get_answer_ids(row["Answers"], uow)

                if existing_question:
                    if (
                        existing_question.answers == answer_ids
                        and existing_question.company_id == company_id
                    ):
                        logger.info(
                            f"Question with title '{question_title}' is up-to-date, skipping."
                        )
                        return

                    logger.info(
                        f"Updating existing question with title '{question_title}'."
                    )
                    updated_question_data = QuestionUpdate(
                        title=question_title,
                    )
                    await QuestionService.update_question(
                        uow,
                        existing_question.id,
                        updated_question_data,
                        current_user_id,
                    )

                else:
                    question_data = QuestionCreate(
                        title=question_title, answers=answer_ids, company_id=company_id
                    )
                    await QuestionService.create_question(
                        uow, question_data, current_user_id
                    )
                    logger.info(f"Created new question with title '{question_title}'.")

            except Exception as e:
                logger.error(
                    f"Error handling question with title '{question_title}': {e}"
                )

    @staticmethod
    async def process_quizzes(
        df_quizzes: pd.DataFrame, uow: UnitOfWork, current_user_id: int
    ):
        """
        Processes the quizzes sheet to create, update, or delete quiz records.

        Args:
            df_quizzes (pd.DataFrame): DataFrame containing quizzes data.
            uow (UnitOfWork): An instance of UnitOfWork for database operations.
            current_user_id (int): The ID of the current user performing the import.
        """
        async with uow:
            existing_quizzes = {q.title: q.id for q in await uow.quiz.find_all()}
            new_quizzes = set(df_quizzes["Title"].dropna().astype(str))

            to_delete = set(existing_quizzes.keys()) - new_quizzes

            if to_delete:
                await DataImportService.delete_quizzes(
                    to_delete, existing_quizzes, uow, current_user_id
                )
            else:
                for index, row in df_quizzes.iterrows():
                    await DataImportService.create_or_update_quiz(
                        row, uow, current_user_id
                    )

    @staticmethod
    async def delete_quizzes(
        to_delete: set, existing_quizzes: dict, uow: UnitOfWork, current_user_id: int
    ):
        """
        Deletes quizzes from the database based on the parsed data.

        Args:
            to_delete (set): Set of quiz titles to be deleted.
            existing_quizzes (dict): Dictionary of existing quizzes with their titles as keys and IDs as values.
            uow (UnitOfWork): An instance of UnitOfWork for database operations.
            current_user_id (int): The ID of the current user performing the import.
        """
        for title in to_delete:
            await QuizService.delete_quiz(uow, existing_quizzes[title], current_user_id)
            logger.info(f"Deleted quiz with title '{title}'")

    @staticmethod
    async def create_or_update_quiz(
        row: pd.Series, uow: UnitOfWork, current_user_id: int
    ):
        """
        Creates or updates a quiz in the database.

        Args:
            row (pd.Series): Series containing data for a single quiz.
            uow (UnitOfWork): An instance of UnitOfWork for database operations.
            current_user_id (int): The ID of the current user performing the import.
        """
        quiz_title = str(row["Title"])
        description = str(row["Description"])
        company_id = int(row["Company ID"])
        async with uow:
            try:
                existing_quiz = await uow.quiz.find_one(title=quiz_title)
                question_ids = await DataImportService.get_question_ids(
                    row["Questions"], uow
                )

                if existing_quiz:
                    if (
                        existing_quiz.description == description
                        and existing_quiz.questions == question_ids
                    ):
                        logger.info(
                            f"Quiz with title '{quiz_title}' is up-to-date, skipping."
                        )
                        return

                    logger.info(f"Updating existing quiz with title '{quiz_title}'.")
                    updated_quiz_data = QuizUpdate(
                        title=quiz_title,
                        description=description,
                    )
                    await QuizService.update_quiz(
                        uow, existing_quiz.id, updated_quiz_data, current_user_id
                    )

                else:
                    quiz_data = QuizCreate(
                        title=quiz_title,
                        description=description,
                        company_id=company_id,
                        questions=question_ids,
                    )
                    await QuizService.create_quiz(uow, quiz_data, current_user_id)
                    logger.info(f"Created new quiz with title '{quiz_title}'.")

            except Exception as e:
                logger.error(f"Error handling quiz with title '{quiz_title}': {e}")

    @staticmethod
    async def get_answer_ids(answers: str, uow: UnitOfWork) -> set:
        """
        Retrieves IDs of answers based on their text.

        Args:
            answers (str): A comma-separated string of answer texts to retrieve IDs for.
            uow (UnitOfWork): An instance of UnitOfWork for database operations.

        Returns:
            set: A set of IDs corresponding to the given answer texts.
        """
        answer_ids = set()
        for answer_text in answers.split(", "):
            answer = await uow.answer.find_one(text=answer_text.strip())
            if answer:
                answer_ids.add(answer.id)
        return answer_ids

    @staticmethod
    async def get_question_ids(questions: str, uow: UnitOfWork) -> list:
        """
        Retrieves IDs of questions based on their titles.

        Args:
            questions (str): A comma-separated string of question titles to retrieve IDs for.
            uow (UnitOfWork): An instance of UnitOfWork for database operations.

        Returns:
            list: A list of IDs corresponding to the given question titles.
        """
        question_ids = []
        for question_title in questions.split(", "):
            question = await uow.question.find_one(title=question_title.strip())
            if question:
                question_ids.append(question.id)
        return question_ids
