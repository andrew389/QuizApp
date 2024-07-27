from app.models import Quiz
from app.uow.repository import SQLAlchemyRepository


class QuizRepository(SQLAlchemyRepository):
    model = Quiz
