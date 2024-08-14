import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.redis_db import redis_connection
from app.routers import (
    me,
    check_connection,
    company,
    invites,
    requests,
    user,
    quiz,
    question,
    answer,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_connection.connect()
    try:
        yield
    finally:
        await redis_connection.disconnect()


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(check_connection.router, prefix=settings.api_v1_prefix)
app.include_router(user.router, prefix=settings.api_v1_prefix)
app.include_router(me.router, prefix=settings.api_v1_prefix)
app.include_router(company.router, prefix=settings.api_v1_prefix)
app.include_router(invites.router, prefix=settings.api_v1_prefix)
app.include_router(requests.router, prefix=settings.api_v1_prefix)
app.include_router(quiz.router, prefix=settings.api_v1_prefix)
app.include_router(question.router, prefix=settings.api_v1_prefix)
app.include_router(answer.router, prefix=settings.api_v1_prefix)
