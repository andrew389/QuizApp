from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import SessionDep
from app.core.logger import logger
from app.db.pg_db import get_async_session
from app.db.redis_db import redis_connection
from app.exceptions.db import BadConnectPostgres, BadConnectRedis

router = APIRouter(tags=["Health Check"])


@router.get("/")
async def health_check():
    """
    Checks the health of the application.

    Returns:
        dict: Status code, detail, and result message.
    """
    logger.debug("Health check endpoint accessed.")
    return {"status_code": 200, "detail": "ok", "result": "working"}


@router.get("/redis")
async def ping_redis():
    """
    Checks the connection to the Redis server.

    Returns:
        dict: Status of Redis connection.

    Raises:
        BadConnectRedis: If there is a connection error with Redis.
    """
    try:
        await redis_connection.ping()
        return {"status": "PONG"}
    except ConnectionError as e:
        logger.error("Redis connection error: %s", e)
        raise BadConnectRedis()


@router.get("/db")
async def ping_db(session: SessionDep):
    """
    Checks the connection to the PostgreSQL database.

    Args:
        session (AsyncSession): The SQLAlchemy async session.

    Returns:
        dict: Status code, detail, and result message.

    Raises:
        BadConnectPostgres: If there is a connection error with PostgreSQL.
    """
    try:
        await session.execute(select(1))
        await session.commit()
        return {"status_code": 200, "detail": "ok", "result": "working"}
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise BadConnectPostgres(str(e))
