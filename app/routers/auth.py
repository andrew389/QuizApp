from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.core.config import settings
from app.core.dependencies import UOWDep
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserResponse, SignInRequest
from app.services.auth import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
async def login_for_access_token(uow: UOWDep, form_data: SignInRequest):
    user: User = await auth_service.authenticate_user(
        uow, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.auth.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"email": user.email},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    return UserResponse(status_code="200", user=current_user)
