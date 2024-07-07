import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.redis_db import redis
from app.routers import check_connection, user

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis.connect()
    try:
        yield
    finally:
        await redis.disconnect()


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(check_connection.router)
app.include_router(user.router)
