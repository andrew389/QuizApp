from app.models.models import Answer
from app.uow.repository import SQLAlchemyRepository


class AnswerRepository(SQLAlchemyRepository):
    model = Answer
