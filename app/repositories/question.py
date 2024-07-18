from app.models.models import Question
from app.uow.repository import SQLAlchemyRepository


class QuestionRepository(SQLAlchemyRepository):
    model = Question
