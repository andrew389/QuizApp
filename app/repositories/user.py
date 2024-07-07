from app.models.user import User
from app.repositories.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = User
