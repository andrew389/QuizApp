from fastapi import HTTPException, status


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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting",
        )
