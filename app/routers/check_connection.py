from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.pg_db import get_async_session
from app.db.redis_db import redis

from app.core.logger import logger

router = APIRouter()


@router.get("/")
async def health_check():
    logger.debug("Health check endpoint accessed.")
    return {"status_code": 200, "detail": "ok", "result": "working"}


@router.get("/redis")
async def ping_redis():
    try:
        await redis.ping()
        return {"status": "PONG"}
    except ConnectionError as e:
        logger.error("Redis connection error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not connect to Redis",
        )


@router.get("/db")
async def ping_db(session: AsyncSession = Depends(get_async_session)):
    try:
        await session.execute(select(1))
        await session.commit()
        return {"status_code": 200, "detail": "ok", "result": "working"}
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database connection error: {str(e)}",
        )
