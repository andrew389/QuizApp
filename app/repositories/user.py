from app.models import User
from app.uow.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    """
    Repository class for managing `User` entities in the database.

    Inherits from `SQLAlchemyRepository` and provides methods specific to `User` entities.
    """

    model = User
