from app.models.models import User
from app.uow.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = User
