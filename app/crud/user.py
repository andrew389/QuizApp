from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.hasher import Hasher
from app.core.logger import logger


class UserCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_users(self, limit: int, offset: int):
        try:
            total = await self.session.execute(select(func.count(User.id)))
            total_users = total.scalar()

            query = await self.session.execute(select(User).offset(offset).limit(limit))
            users = query.scalars().all()

            logger.info(
                f"Retrieved {len(users)} users with limit {limit} and offset {offset}"
            )

            return {
                "users": users,
                "total": total_users,
                "limit": limit,
                "offset": offset,
            }
        except Exception as e:
            logger.error(f"Failed to retrieve all users: {e}")
            raise

    async def get_user_by_id(self, user_id: int):
        try:
            user = await self.session.get(User, user_id)
            if user:
                logger.info(f"User retrieved: {user.username}")
            else:
                logger.warning(f"User with id {user_id} not found")
            return user
        except Exception as e:
            logger.error(f"Failed to retrieve user with id {user_id}: {e}")
            raise

    async def create_new_user(self, user_create: UserCreate):
        try:
            hashed_password = Hasher.hash_password(user_create.password)
            new_user = User(
                username=user_create.username,
                email=user_create.email,
                hashed_password=hashed_password,
            )

            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)

            logger.info(f"User created: {new_user.username}")
            return new_user
        except Exception as e:
            logger.error(f"Failed to create new user: {e}")
            raise

    async def update_user_by_id(self, user_id: int, user_update: UserUpdate):
        try:
            user = await self.session.get(User, user_id)

            if user:
                if user_update.username:
                    user.username = user_update.username
                if user_update.email:
                    user.email = user_update.email
                if user_update.password:
                    user.hashed_password = Hasher.hash_password(user_update.password)

                await self.session.commit()
                await self.session.refresh(user)

                logger.info(f"User updated: {user.username}")
                return user

            logger.warning(f"User with id {user_id} not found")
            return None
        except Exception as e:
            logger.error(f"Failed to update user with id {user_id}: {e}")
            raise

    async def delete_user_by_id(self, user_id: int):
        try:
            user = await self.session.get(User, user_id)

            if user:
                await self.session.delete(user)
                await self.session.commit()

                logger.info(f"User deleted: {user.username}")
                return user

            logger.warning(f"User with id {user_id} not found")
            return None
        except Exception as e:
            logger.error(f"Failed to delete user with id {user_id}: {e}")
            raise
