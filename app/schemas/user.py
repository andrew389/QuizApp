from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
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
    email: EmailStr
    password: str
    firstname: str
    lastname: str
    city: str
    phone: str
    avatar: str


class UserUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    password: Optional[str] = None


class UserDetail(UserBase):
    password: str


class UserResponse(BaseModel):
    user: Optional[UserDetail] = None


class SignInRequest(BaseModel):
    email: str
    password: str


class SignUpRequest(UserCreate):
    password1: str
    password2: str

    @field_validator("password2")
    def passwords_match(cls, v, values, **kwargs):
        if "password1" in values and v != values["password1"]:
            raise ValueError("passwords do not match")
        return v


class UsersListResponse(BaseModel):
    users: List[UserBase]
    total: int
