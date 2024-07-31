from datetime import datetime

from pydantic import BaseModel, field_validator


class Token(BaseModel):
    """
    Schema for an authentication token.

    Attributes:
        access_token (str): The access token string.
        token_type (str): The type of the token (e.g., "Bearer").
        expiration (float): The expiration time of the token as a timestamp.
    """

    access_token: str
    token_type: str
    expiration: float

    @field_validator("expiration", mode="before")
    def parse_expiration(cls, value):
        """
        Parses the expiration value to a timestamp if it's a datetime object.

        Args:
            value (datetime or float): The expiration time.

        Returns:
            float: The expiration time as a timestamp.
        """
        if isinstance(value, datetime):
            return value.timestamp()
        return value

    @field_validator("expiration", mode="after")
    def format_expiration(cls, value):
        """
        Formats the expiration value to a datetime object if it's a timestamp.

        Args:
            value (int or float): The expiration time as a timestamp.

        Returns:
            datetime: The expiration time as a datetime object.
        """
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value)
        return value


class TokenData(BaseModel):
    """
    Schema for token data.

    Attributes:
        email (str): The email associated with the token.
        token (str): The token string.
    """

    email: str
    token: str
