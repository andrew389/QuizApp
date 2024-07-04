from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.pg_db import get_async_session
from db.redis_db import redis

router = APIRouter()


@router.get("/")
async def health_check():
    return {"status_code": 200, "detail": "ok", "result": "working"}


@router.get("/redis")
async def read_items(item_name: str):
    return dict(id=redis.read(key=item_name))


@router.get("/db")
async def ping_db(session: AsyncSession = Depends(get_async_session)):
    try:
        await session.execute(select(1))
        await session.commit()
        return {"db_ping": "Database is reachable"}
    except Exception as e:
        return {"db_ping": f"Database connection error: {str(e)}"}
