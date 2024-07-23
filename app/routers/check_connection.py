from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.pg_db import get_async_session
from app.db.redis_db import redis

from app.core.logger import logger
from app.exceptions.db import BadConnectRedis, BadConnectPostgres

router = APIRouter(tags=["Health Check"])


@router.get("/")
async def health_check():
    """
    Health check endpoint to verify that the service is running.

    Returns:
        dict: A dictionary containing the status code, detail, and result of the health check.
    """
    logger.debug("Health check endpoint accessed.")
    return {"status_code": 200, "detail": "ok", "result": "working"}


@router.get("/redis")
async def ping_redis():
    """
    Checks the connectivity to the Redis server by sending a ping command.

    Returns:
        dict: A dictionary containing the status of the Redis connection.

    Raises:
        BadConnectRedis: If there is a connection error with Redis.
    """
    try:
        await redis.ping()
        return {"status": "PONG"}
    except ConnectionError as e:
        logger.error("Redis connection error: %s", e)
        raise BadConnectRedis()


@router.get("/db")
async def ping_db(session: AsyncSession = Depends(get_async_session)):
    """
    Checks the connectivity to the PostgreSQL database by executing a simple query.

    Args:
        session (AsyncSession): The database session used to execute the query.

    Returns:
        dict: A dictionary containing the status code, detail, and result of the database connection check.

    Raises:
        BadConnectPostgres: If there is a connection error with the PostgreSQL database.
    """
    try:
        await session.execute(select(1))
        await session.commit()
        return {"status_code": 200, "detail": "ok", "result": "working"}
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise BadConnectPostgres(str(e))
