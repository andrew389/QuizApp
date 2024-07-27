from app.models import User
from app.uow.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = User
