import pandas as pd
from fastapi import UploadFile
from app.core.logger import logger
from app.schemas.answer import AnswerCreate, AnswerBase
from app.schemas.question import QuestionCreate, QuestionBase
from app.schemas.quiz import QuizCreate, QuizBase, QuizUpdate
from app.uow.unitofwork import UnitOfWork


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

            answers_mapping = await DataImportService.create_answers(
                df_answers, uow, current_user_id
            )
            questions_mapping = await DataImportService.create_questions(
                df_questions, answers_mapping, uow, current_user_id
            )
            await DataImportService.create_or_update_quizzes(
                df_quizzes, questions_mapping, uow, current_user_id
            )

        except Exception as e:
            logger.error(f"Error parsing Excel file: {e}")
            raise

    @staticmethod
    async def create_answers(
        df_answers: pd.DataFrame, uow: UnitOfWork, current_user_id: int
    ):
        answers_mapping = {}
        for index, row in df_answers.iterrows():
            answer_id = int(row["Answer ID"])
            try:
                # Check if answer already exists
                existing_answer = await uow.answer.find_one(id=answer_id)
                if existing_answer:
                    logger.info(f"Answer with ID {answer_id} already exists, skipping.")
                    continue

                answer_data = AnswerBase(
                    id=answer_id,
                    text=str(row["Text"]),
                    is_correct=bool(row["Is Correct"]),
                    company_id=int(row["Company ID"]),
                )
                # Manually create the Answer record with the specified ID
                await uow.answer.add_one(answer_data.model_dump())
                answers_mapping[answer_id] = (
                    answer_id  # Map the Excel ID to the same ID
                )
            except Exception as e:
                logger.error(f"Error creating answer with ID {answer_id}: {e}")
        return answers_mapping

    @staticmethod
    async def create_questions(
        df_questions: pd.DataFrame,
        answers_mapping: dict,
        uow: UnitOfWork,
        current_user_id: int,
    ):
        questions_mapping = {}
        for index, row in df_questions.iterrows():
            question_id = int(row["Question ID"])
            try:
                # Check if question already exists
                existing_question = await uow.question.find_one(id=question_id)
                if existing_question:
                    logger.info(
                        f"Question with ID {question_id} already exists, skipping."
                    )
                    continue

                answer_ids = str(row["Answers"]).split(",")
                question_data = QuestionCreate(
                    title=str(row["Title"]),
                    company_id=int(row["Company ID"]),
                    answers={
                        answers_mapping.get(int(aid))
                        for aid in answer_ids
                        if int(aid) in answers_mapping
                    },
                )
                # Manually create the Question record with the specified ID
                new_question = QuestionBase(**question_data.__dict__, id=question_id)
                await uow.question.add_one(new_question)
                questions_mapping[question_id] = (
                    question_id  # Map the Excel ID to the same ID
                )
            except Exception as e:
                logger.error(f"Error creating question with ID {question_id}: {e}")
        return questions_mapping

    @staticmethod
    async def create_or_update_quizzes(
        df_quizzes: pd.DataFrame,
        questions_mapping: dict,
        uow: UnitOfWork,
        current_user_id: int,
    ):
        for index, row in df_quizzes.iterrows():
            quiz_id = int(row["Quiz ID"])
            try:
                # Check if quiz already exists
                existing_quiz = await uow.quiz.find_one(id=quiz_id)

                if not existing_quiz:
                    # Create new quiz
                    question_ids = str(row["Questions"]).split(",")
                    quiz_data = QuizCreate(
                        title=str(row["Title"]),
                        description=str(row["Description"]),
                        frequency=(
                            int(row["Frequency"])
                            if not pd.isna(row["Frequency"])
                            else 0
                        ),
                        company_id=int(row["Company ID"]),
                        questions=[
                            questions_mapping.get(int(qid))
                            for qid in question_ids
                            if int(qid) in questions_mapping
                        ],
                    )
                    # Manually create the Quiz record with the specified ID
                    new_quiz = QuizBase(**quiz_data.__dict__, id=quiz_id)
                    await uow.quiz.add_one(new_quiz)
                else:
                    # Update existing quiz if necessary
                    if pd.isna(row["Frequency"]) and pd.isna(row["Questions"]):
                        quiz_update_data = QuizUpdate(
                            title=str(row["Title"]),
                            description=str(row["Description"]),
                        )
                        # Implement the update logic using uow directly if needed
                        await uow.quiz.update_one(
                            id=quiz_id, update_data=quiz_update_data
                        )
                    else:
                        logger.info(
                            f"Quiz with ID {quiz_id} already exists and has full data, skipping."
                        )
            except Exception as e:
                logger.error(f"Error creating or updating quiz with ID {quiz_id}: {e}")
