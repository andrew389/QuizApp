from app.core.logger import logger
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserDetail,
    UsersListResponse,
    UserUpdate,
)
from app.uow.unitofwork import IUnitOfWork
from app.utils.hasher import Hasher


class UserService:
    @staticmethod
    async def add_user(uow: IUnitOfWork, user: UserCreate) -> UserBase:
        async with uow:
            existing_user = await uow.user.find_one(email=user.email)
            if existing_user:
                logger.error("User with this email already exists")
                raise ValueError()

            user_dict = user.model_dump()
            user_dict["password"] = Hasher.hash_password(user_dict.pop("password"))

            user_model = await uow.user.add_one(user_dict)
            await uow.commit()

        return UserBase(**user_model.__dict__)

    @staticmethod
    async def get_users(
        uow: IUnitOfWork, skip: int = 0, limit: int = 10
    ) -> UsersListResponse:
        async with uow:
            users = await uow.user.find_all(skip=skip, limit=limit)
            user_list = UsersListResponse(
                users=[UserBase(**user.__dict__) for user in users], total=len(users)
            )
            return user_list

    @staticmethod
    async def get_user_by_id(uow: IUnitOfWork, user_id: int) -> UserBase:
        async with uow:
            user_model = await uow.user.find_one(id=user_id)
            if user_model:
                return UserBase(**user_model.__dict__)

    @staticmethod
    async def get_user_by_username(uow: IUnitOfWork, username: str) -> UserDetail:
        async with uow:
            user_model = await uow.user.find_one(username=username)
            if user_model:
                return UserDetail(**user_model.__dict__)

    @staticmethod
    async def get_user_by_email(uow: IUnitOfWork, email: str) -> UserDetail:
        async with uow:
            user_model = await uow.user.find_one(email=email)
            if user_model:
                return UserDetail(**user_model.__dict__)

    @staticmethod
    async def validate_user_update(
        uow: IUnitOfWork, user_id: int, user_update: UserUpdate
    ) -> UserUpdate:
        current_user = await uow.user.find_one(id=user_id)
        if not current_user:
            raise NotFoundException()

        user_data = user_update.model_dump()
        fields_to_check = user_data.keys()
        default_values = ["string"]

        for field_name in fields_to_check:
            field_value = user_data[field_name]
            if field_value in [None, *default_values]:
                setattr(user_update, field_name, getattr(current_user, field_name))

        return user_update

    @staticmethod
    async def update_user(
        uow: IUnitOfWork, current_user_id: int, user_id: int, user_update: UserUpdate
    ) -> UserDetail:
        async with uow:
            if current_user_id != user_id:
                raise UnAuthorizedException()

            user_update = await UserService.validate_user_update(
                uow, user_id, user_update
            )
            user_dict = user_update.model_dump()
            user_dict["id"] = user_id

            await uow.user.edit_one(user_id, user_dict)
            await uow.commit()
            updated_user = await uow.user.find_one(id=user_id)
            return UserDetail(**updated_user.__dict__)

    @staticmethod
    async def deactivate_user(
        uow: IUnitOfWork, user_id: int, current_user_id: int
    ) -> UserDetail:
        async with uow:
            if current_user_id != user_id:
                raise UnAuthorizedException()

            user_model = await uow.user.find_one(id=user_id)
            if not user_model:
                raise NotFoundException()

            user_model.is_active = False
            await uow.user.edit_one(user_id, {"is_active": False})
            await uow.commit()
            return UserDetail(**user_model.__dict__)
