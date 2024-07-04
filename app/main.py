from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.redis_db import redis

from app.routers import check_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.start_connection()
    redis.write(key="whisky", value=0)

    yield
    redis.close_connection()


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:8000",
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
