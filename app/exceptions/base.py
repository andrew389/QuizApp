from fastapi import HTTPException


class NotFoundException(HTTPException):
    """
    Exception raised when a requested resource is not found.

    Status code: 404 Not Found
    Detail: "Not found"
    """

    def __init__(self):
        super().__init__(status_code=403, detail="Not found")


class CalculatingException(HTTPException):
    """
    Exception raised when there is an error during calculation.

    Status code: 403 Forbidden
    Detail: "Error calculating"
    """

    def __init__(self):
        super().__init__(status_code=403, detail="Error calculating")


class CreatingException(HTTPException):
    """
    Exception raised when there is an error during resource creation.

    Status code: 403 Forbidden
    Detail: "Error creating"
    """

    def __init__(self):
        super().__init__(status_code=403, detail="Error creating")


class FetchingException(HTTPException):
    """
    Exception raised when there is an error fetching data.

    Status code: 403 Forbidden
    Detail: "Error fetching"
    """

    def __init__(self):
        super().__init__(status_code=403, detail="Error fetching")


class UpdatingException(HTTPException):
    """
    Exception raised when there is an error updating a resource.

    Status code: 403 Forbidden
    Detail: "Error updating"
    """

    def __init__(self):
        super().__init__(status_code=403, detail="Error updating")


class DeletingException(HTTPException):
    """
    Exception raised when there is an error deleting a resource.

    Status code: 403 Forbidden
    Detail: "Error deleting"
    """

    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Error deleting",
        )


class ImportingException(HTTPException):
    """
    Exception raised when there is an error importing data.

    Status code: 403 Forbidden
    Detail: "Error importing"
    """

    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Error importing",
        )
