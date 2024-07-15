from fastapi import HTTPException, status


class BadConnectRedis(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not connect to Redis",
        )


class BadConnectPostgres(HTTPException):
    def __init__(self, exception_message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database connection error: {exception_message}",
        )
