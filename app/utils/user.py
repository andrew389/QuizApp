from fastapi import Request

import secrets
import string
from datetime import datetime

from app.schemas.pagination import PaginationLinks
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
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    return user_create


def get_pagination_urls(
    request: Request, skip: int, limit: int, total_users: int
) -> PaginationLinks:
    base_url = str(request.url).split("?")[0]

    next_url = (
        f"{base_url}?skip={skip + limit}&limit={limit}"
        if skip + limit < total_users
        else None
    )
    previous_url = (
        f"{base_url}?skip={max(skip - limit, 0)}&limit={limit}" if skip > 0 else None
    )
    return PaginationLinks(next=next_url, previous=previous_url)
