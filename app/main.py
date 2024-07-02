from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def home():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }
