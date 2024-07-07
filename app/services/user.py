from app.schemas.user import UserCreate, UsersList, UserBase, UserDetail, UserUpdate
from app.utils.hasher import Hasher
from app.repositories.unitofwork import IUnitOfWork


class UserService:
    @staticmethod
    async def add_user(uow: IUnitOfWork, user: UserCreate) -> UserDetail:
        user_dict = user.model_dump()
        user_dict["hashed_password"] = Hasher.hash_password(
            user_dict.pop("hashed_password")
        )
        async with uow:
            user_id = await uow.user.add_one(user_dict)
            await uow.commit()
            user = await uow.user.find_one(id=user_id)
            return UserDetail(**user.__dict__)

    @staticmethod
    async def get_users(uow: IUnitOfWork) -> UsersList:
        async with uow:
            users = await uow.user.find_all()
            user_list = UsersList(users=[UserBase(**user.__dict__) for user in users])
            return user_list

    @staticmethod
    async def get_user_by_id(uow: IUnitOfWork, user_id: int) -> UserDetail:
        async with uow:
            user = await uow.user.find_one(id=user_id)
            if user:
                return UserDetail(**user.__dict__)

    @staticmethod
    async def update_user(
        uow: IUnitOfWork, user_id: int, user_update: UserUpdate
    ) -> UserDetail:
        async with uow:
            user = await uow.user.find_one(id=user_id)

            user_dict = user_update.model_dump()
            user_dict["id"] = user_id
            if "username" in user_dict and user_dict["username"] == "string":
                user_dict["username"] = user.username
            if "email" in user_dict and user_dict["email"] == "user@example.com":
                user_dict["email"] = user.email
            if (
                "hashed_password" in user_dict
                and user_dict["hashed_password"] == "string"
            ):
                user_dict["hashed_password"] = user.hashed_password

            await uow.user.edit_one(user_id, user_dict)
            await uow.commit()
            updated_user = await uow.user.find_one(id=user_id)
            return UserDetail(**updated_user.__dict__)

    @staticmethod
    async def delete_user(uow: IUnitOfWork, user_id: int) -> int:
        async with uow:
            deleted_user_id = await uow.user.delete_one(user_id)
            await uow.commit()
            return deleted_user_id
