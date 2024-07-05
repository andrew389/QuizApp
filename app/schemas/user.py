from typing import Optional, List

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    username: str
    email: EmailStr


class UserResponse(BaseModel):
    user: Optional[UserBase] = None


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UsersList(BaseModel):
    users: List[UserBase]


class UserDetail(UserBase):
    pass


class SignIn(BaseModel):
    username: str
    password: str


class SignUp(BaseModel):
    username: str
    email: EmailStr
    password: str
