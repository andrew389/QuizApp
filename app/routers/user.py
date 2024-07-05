from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.pg_db import get_async_session
from app.schemas.user import UserResponse, UserCreate, UserUpdate, UsersList, UserDetail
from app.crud.user import UserCRUD

router = APIRouter(prefix="/user")


@router.get("/all", response_model=UsersList)
async def get_all_users(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
):
    user_crud = UserCRUD(session)
    return await user_crud.get_all_users(limit, offset)


@router.get("/{user_id}", response_model=UserDetail)
async def get_user_by_id(
    user_id: int, session: AsyncSession = Depends(get_async_session)
):
    user_crud = UserCRUD(session)
    user = await user_crud.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/new", response_model=UserResponse)
async def create_new_user(
    user_create: UserCreate, session: AsyncSession = Depends(get_async_session)
):
    user_crud = UserCRUD(session)
    new_user = await user_crud.create_new_user(user_create)
    return {"msg": "User created successfully", "user": new_user}


@router.put("/update/{user_id}", response_model=UserResponse)
async def update_user_by_id(
    user_id: int,
    user_update: UserUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    user_crud = UserCRUD(session)
    user = await user_crud.update_user_by_id(user_id, user_update)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"msg": "User updated successfully", "user": user}


@router.delete("/delete/{user_id}", response_model=UserResponse)
async def delete_user_by_id(
    user_id: int, session: AsyncSession = Depends(get_async_session)
):
    user_crud = UserCRUD(session)
    user = await user_crud.delete_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"msg": "User deleted successfully"}
