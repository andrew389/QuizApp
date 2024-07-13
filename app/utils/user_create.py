import secrets
import string
from datetime import datetime

from app.uow.unitofwork import UnitOfWork
from app.schemas.user import UserCreate
from app.services.user import UserService


def generate_random_password(length: int = 12) -> str:
    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(characters) for i in range(length))
    return password


async def create_user(uow: UnitOfWork, email: str):
    random_password = generate_random_password()
    user_create = UserCreate(
        username=email.split("@")[0],
        email=email,
        password=random_password,
        firstname="First",
        lastname="Last",
        city="City",
        phone="1234567890",
        avatar="",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    return await UserService.add_user(uow, user_create)
