import secrets
import string
from datetime import datetime

from app.schemas.user import UserCreate


def generate_random_password(length: int = 12) -> str:
    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(characters) for i in range(length))
    return password


def remove_timezone(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def create_user(email: str):
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
    return user_create
