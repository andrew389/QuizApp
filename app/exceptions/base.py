from fastapi import HTTPException


class NotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Not found")


class CalculatingException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Error calculating")


class CreatingException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Error creating")


class FetchingException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Error fetching")


class UpdatingException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Error updating")


class DeletingException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Error deleting",
        )
