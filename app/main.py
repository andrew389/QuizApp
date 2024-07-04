from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.redis_db import redis
from routers import check_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis.connect()
    try:
        yield
    finally:
        await redis.disconnect()


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:8010",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(check_connection.router)
