from fastapi import HTTPException, status


class BadConnectRedis(HTTPException):
    """
    Exception raised when there is an issue connecting to Redis.

    Status code: 400 Bad Request
    Detail: "Could not connect to Redis"
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not connect to Redis",
        )


class BadConnectPostgres(HTTPException):
    """
    Exception raised when there is a connection error with PostgreSQL.

    Status code: 400 Bad Request
    Detail: "Database connection error: {exception_message}"
    """

    def __init__(self, exception_message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database connection error: {exception_message}",
        )
