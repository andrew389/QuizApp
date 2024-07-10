from fastapi import HTTPException
from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
    field_validator,
    Field,
    model_validator,
)
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    username: str
    email: EmailStr
    is_active: bool
    firstname: str
    lastname: str
    city: str
    phone: str
    avatar: str
    is_superuser: bool
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    firstname: str
    lastname: str
    city: str
    phone: str
    avatar: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserUpdate(BaseModel):
    updated_at: datetime = Field(default_factory=datetime.now)
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    hashed_password: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None


class UserDetail(UserBase):
    hashed_password: Optional[str] = None


class UserResponse(BaseModel):
    user: Optional[UserDetail] = None


class SignInRequest(BaseModel):
    username: str
    password: str


class SignUpRequest(UserCreate):
    username: str
    email: EmailStr
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
