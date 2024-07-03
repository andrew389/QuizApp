from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from db.redis_db import redis_client, get_redis
from utils.config import settings

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
async def health_check():
    return {
        "status_code": settings.postgres_db_port,
        "detail": "ok",
        "result": "working"
    }

@app.on_event("startup")
async def startup():
    await redis_client.initialize()

@app.on_event("shutdown")
async def shutdown():
    await redis_client.close()

@app.get("/redis/")
async def read_redis(redis=Depends(get_redis)):
    await redis.set("key", "value")
    value = await redis.get("key")
    return {"key": value.decode("utf-8")}