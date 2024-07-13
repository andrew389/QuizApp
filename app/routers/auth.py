from datetime import timedelta

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.dependencies import UOWDep, AuthServiceDep
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserResponse, SignInRequest
from app.exceptions.auth import AuthenticationException

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
async def login_for_access_token(
    uow: UOWDep, form_data: SignInRequest, auth_service: AuthServiceDep
):
    user: User = await auth_service.authenticate_user(
        uow, form_data.username, form_data.password
    )
    if not user:
        raise AuthenticationException()
    access_token_expires = timedelta(minutes=settings.auth.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"email": user.email},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(AuthServiceDep.get_current_user)):
    return UserResponse(status_code="200", user=current_user)
