from fastapi import HTTPException, status


class AuthenticationException(HTTPException):
    """
    Exception raised for incorrect username or password during authentication.

    Status code: 401 Unauthorized
    Detail: "Incorrect username or password"
    Headers: {"WWW-Authenticate": "Bearer"}
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


class NotAuthenticatedException(HTTPException):
    """
    Exception raised when a user is not authenticated.

    Status code: 401 Unauthorized
    Detail: "Not authenticated"
    Headers: {"WWW-Authenticate": "Bearer"}
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UnAuthorizedException(HTTPException):
    """
    Exception raised when a user is unauthorized to perform an action.

    Status code: 401 Unauthorized
    Detail: "You are unauthorized"
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are unauthorized",
        )


class ValidateCredentialsException(HTTPException):
    """
    Exception raised when credentials could not be validated.

    Status code: 401 Unauthorized
    Detail: "Could not validate credentials"
    Headers: {"WWW-Authenticate": "Bearer"}
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
