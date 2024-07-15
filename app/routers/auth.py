from fastapi import APIRouter, Depends, status

from app.core.dependencies import UOWDep, AuthServiceDep
from app.models.models import User
from app.schemas.token import Token
from app.schemas.user import UserResponse, SignInRequest
from app.exceptions.auth import AuthenticationException

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
async def login_for_access_token(
    uow: UOWDep, form_data: SignInRequest, auth_service: AuthServiceDep
):
    user = await auth_service.authenticate_user(
        uow, form_data.email, form_data.password
    )
    if not user:
        raise AuthenticationException()
    access_token, expiration = auth_service.create_access_token(
        data={"email": user.email}
    )
    return Token(access_token=access_token, token_type="bearer", expiration=expiration)


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def read_users_me(current_user: User = Depends(AuthServiceDep.get_current_user)):
    return UserResponse(user=current_user)
