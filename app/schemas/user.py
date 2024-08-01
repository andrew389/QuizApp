from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.pagination import PaginationLinks


class UserBase(BaseModel):
    """
    Base schema for user data.
    """

    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = Field(None, description="The unique identifier of the user.")
    email: EmailStr = Field(..., description="The email address of the user.")
    is_active: bool = Field(..., description="Indicates whether the user is active.")
    firstname: str = Field(..., description="The first name of the user.")
    lastname: str = Field(..., description="The last name of the user.")
    city: str = Field(..., description="The city where the user resides.")
    phone: str = Field(..., description="The phone number of the user.")
    avatar: str = Field(..., description="URL or path to the user's avatar image.")
    is_superuser: bool = Field(
        ..., description="Indicates whether the user has superuser privileges."
    )


class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    """

    email: EmailStr = Field(..., description="The email address of the user.")
    password: str = Field(..., description="The password for the user.")
    firstname: str = Field(..., description="The first name of the user.")
    lastname: str = Field(..., description="The last name of the user.")
    city: str = Field(..., description="The city where the user resides.")
    phone: str = Field(..., description="The phone number of the user.")
    avatar: str = Field(..., description="URL or path to the user's avatar image.")


class UserUpdate(BaseModel):
    """
    Schema for updating user information.
    """

    firstname: Optional[str] = Field(
        None, description="The updated first name of the user."
    )
    lastname: Optional[str] = Field(
        None, description="The updated last name of the user."
    )
    password: Optional[str] = Field(
        None, description="The updated password for the user."
    )


class UserDetail(UserBase):
    """
    Schema for detailed user information, including the password.
    """

    password: str = Field(..., description="The password of the user.")


class UserResponse(BaseModel):
    """
    Schema for user response containing user data.
    """

    user: Optional[UserBase] = Field(None, description="The user data.")


class SignInRequest(BaseModel):
    """
    Schema for sign-in request.
    """

    email: str = Field(..., description="The email address of the user.")
    password: str = Field(..., description="The password of the user.")


class SignUpRequest(UserCreate):
    """
    Schema for sign-up request, including password confirmation.
    """

    password1: str = Field(..., description="The first password input.")
    password2: str = Field(
        ..., description="The second password input for confirmation."
    )

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
    """

    links: PaginationLinks = Field(
        ..., description="Pagination links for navigating through pages."
    )
    users: List[UserBase] = Field(..., description="The list of users.")
    total: int = Field(..., description="The total number of users.")
