from fastapi import HTTPException, status


class NotFoundUserException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User not found")


class UserCannotChangeEmailException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="User cannot change email")


class CreatingUserException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="User cannot change email")


class FetchingUserException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="User cannot change email")


class UpdatingUserException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="User cannot change email")


class DeletingUserException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user",
        )
