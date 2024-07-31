from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.schemas.pagination import PaginationLinks


class UserBase(BaseModel):
    """
    Base schema for user data.

    Attributes:
        id (Optional[int]): The unique identifier of the user.
        email (EmailStr): The email address of the user.
        is_active (bool): Indicates whether the user is active.
        firstname (str): The first name of the user.
        lastname (str): The last name of the user.
        city (str): The city where the user resides.
        phone (str): The phone number of the user.
        avatar (str): URL or path to the user's avatar image.
        is_superuser (bool): Indicates whether the user has superuser privileges.
    """

    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    email: EmailStr
    is_active: bool
    firstname: str
    lastname: str
    city: str
    phone: str
    avatar: str
    is_superuser: bool


class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    Attributes:
        email (EmailStr): The email address of the user.
        password (str): The password for the user.
        firstname (str): The first name of the user.
        lastname (str): The last name of the user.
        city (str): The city where the user resides.
        phone (str): The phone number of the user.
        avatar (str): URL or path to the user's avatar image.
    """

    email: EmailStr
    password: str
    firstname: str
    lastname: str
    city: str
    phone: str
    avatar: str


class UserUpdate(BaseModel):
    """
    Schema for updating user information.

    Attributes:
        firstname (Optional[str]): The updated first name of the user.
        lastname (Optional[str]): The updated last name of the user.
        password (Optional[str]): The updated password for the user.
    """

    firstname: Optional[str] = None
    lastname: Optional[str] = None
    password: Optional[str] = None


class UserDetail(UserBase):
    """
    Schema for detailed user information, including the password.

    Attributes:
        password (str): The password of the user.
    """

    password: str


class UserResponse(BaseModel):
    """
    Schema for user response containing user data.

    Attributes:
        user (Optional[UserBase]): The user data.
    """

    user: Optional[UserBase] = None


class SignInRequest(BaseModel):
    """
    Schema for sign-in request.

    Attributes:
        email (str): The email address of the user.
        password (str): The password of the user.
    """

    email: str
    password: str


class SignUpRequest(UserCreate):
    """
    Schema for sign-up request, including password confirmation.

    Attributes:
        password1 (str): The first password input.
        password2 (str): The second password input for confirmation.
    """

    password1: str
    password2: str

    @field_validator("password2")
    def passwords_match(cls, v, values, **kwargs):
        """
        Validates that both password fields match.

        Args:
            v (str): The value of password2.
            values (dict): A dictionary of values already processed.

        Returns:
            str: The value of password2 if passwords match.

        Raises:
            ValueError: If password1 and password2 do not match.
        """
        if "password1" in values and v != values["password1"]:
            raise ValueError("Passwords do not match")
        return v


class UsersListResponse(BaseModel):
    """
    Schema for the list of users with pagination links.

    Attributes:
        links (PaginationLinks): Pagination links for navigating through pages.
        users (List[UserBase]): The list of users.
        total (int): The total number of users.
    """

    links: PaginationLinks
    users: List[UserBase]
    total: int
