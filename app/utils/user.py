import secrets
import string
from datetime import datetime
from app.schemas.user import UserCreate


def generate_random_password(length: int = 12) -> str:
    """
    Generate a random password with the specified length.
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(characters) for _ in range(length))
    return password


def create_user(email: str) -> UserCreate:
    """
    Create a UserCreate object with a random password and default user details.
    """
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
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    return user_create
