from fastapi import Request
import secrets
import string
from datetime import datetime
from app.schemas.pagination import PaginationLinks
from app.schemas.user import UserCreate


def generate_random_password(length: int = 12) -> str:
    """
    Generate a random password with the specified length.

    Args:
        length (int): The length of the generated password. Default is 12.

    Returns:
        str: A randomly generated password.
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(characters) for _ in range(length))
    return password


def create_user(email: str) -> UserCreate:
    """
    Create a UserCreate object with a random password and default user details.

    Args:
        email (str): The email address of the user.

    Returns:
        UserCreate: An object containing the new user's details.
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
    """
    Generate pagination URLs for navigating through a list of users.

    Args:
        request (Request): The FastAPI request object.
        skip (int): The number of items to skip (used for pagination).
        limit (int): The number of items to retrieve per page.
        total_users (int): The total number of users available.

    Returns:
        PaginationLinks: An object containing the next and previous pagination URLs.
    """
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


def filter_data(data) -> dict:
    """
    Filter out SQLAlchemy instance state from the data dictionary.

    Args:
        data: The SQLAlchemy instance whose state is to be filtered out.

    Returns:
        dict: A dictionary representation of the instance excluding the internal state.
    """
    return {k: v for k, v in data.__dict__.items() if k != "_sa_instance_state"}
