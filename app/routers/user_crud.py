from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.db.pg_db import get_async_session

from app.core.logger import logger

from app.models.user import User
from app.schemas.user import UserResponse, UserCreate, UserUpdate, UsersList, UserDetail

router = APIRouter(prefix="/user")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/all", response_model=UsersList)
async def get_all_users(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        total = await session.execute(select(func.count(User.id)))
        total_users = total.scalar()

        query = await session.execute(select(User).offset(offset).limit(limit))
        users = query.scalars().all()

        return {"users": users, "total": total_users, "limit": limit, "offset": offset}
    except Exception as e:
        logger.error(f"Failed to retrieve all users: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve all users")


@router.get("/{user_id}", response_model=UserDetail)
async def get_user_by_id(
    user_id: int, session: AsyncSession = Depends(get_async_session)
):
    try:
        user = await session.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve user with id {user_id}: {e}")
        raise HTTPException(
            status_code=404, detail=f"Failed to retrieve user with id {user_id}"
        )


@router.post("/new", response_model=UserResponse)
async def create_new_user(
    user_create: UserCreate, session: AsyncSession = Depends(get_async_session)
):
    try:
        hashed_password = pwd_context.hash(user_create.password)
        new_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return {"msg": "User created successfully", "user": new_user}
    except Exception as e:
        logger.error(f"Failed to create new user: {e}")
        raise HTTPException(status_code=404, detail="Failed to create new user")


@router.put("/update/{user_id}", response_model=UserResponse)
async def update_user_by_id(
    user_id: int,
    user_update: UserUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        user = await session.get(User, user_id)

        if user:
            if user_update.username:
                user.username = user_update.username
            if user_update.email:
                user.email = user_update.email
            if user_update.password:
                user.hashed_password = pwd_context.hash(user_update.password)

            await session.commit()
            await session.refresh(user)
            return {"msg": "User updated successfully", "user": user}

        raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user with id {user_id}: {e}")
        raise HTTPException(
            status_code=404, detail=f"Failed to update user with id {user_id}"
        )


@router.delete("/delete/{user_id}", response_model=UserResponse)
async def delete_user_by_id(
    user_id: int, session: AsyncSession = Depends(get_async_session)
):
    try:
        user = await session.get(User, user_id)

        if user:
            await session.delete(user)
            await session.commit()
            return {"msg": "User deleted successfully"}

        raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user with id {user_id}: {e}")
        raise HTTPException(
            status_code=404, detail=f"Failed to delete user with id {user_id}"
        )
