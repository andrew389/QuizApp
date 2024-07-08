from typing import Optional, List

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    username: str
    email: EmailStr


class UserResponse(BaseModel):
    status_code: str
    user: Optional[UserBase] = None


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    hashed_password: Optional[str] = None


class UsersList(BaseModel):
    users: List[UserBase]


class UserDetail(UserBase):
    hashed_password: Optional[str] = None


class SignIn(BaseModel):
    username: str
    hashed_password: str


class SignUp(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
