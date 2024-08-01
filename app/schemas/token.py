from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class Token(BaseModel):
    """
    Schema for an authentication token.
    """

    access_token: str = Field(..., description="The access token string.")
    token_type: str = Field(..., description="The type of the token (e.g., 'Bearer').")
    expiration: float = Field(
        ...,
        description="The expiration time of the token as a timestamp (seconds since the epoch).",
    )

    @field_validator("expiration", mode="before")
    def parse_expiration(cls, value):
        """
        Parses the expiration value to a timestamp if it's a datetime object.

        Args:
            value (datetime or float): The expiration time, either as a datetime object or a timestamp.

        Returns:
            float: The expiration time as a timestamp (seconds since the epoch).
        """
        if isinstance(value, datetime):
            return value.timestamp()
        return value

    @field_validator("expiration", mode="after")
    def format_expiration(cls, value):
        """
        Formats the expiration value to a datetime object if it's a timestamp.

        Args:
            value (int or float): The expiration time as a timestamp (seconds since the epoch).

        Returns:
            datetime: The expiration time as a datetime object.
        """
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value)
        return value


class TokenData(BaseModel):
    """
    Schema for token data.
    """

    email: str = Field(..., description="The email associated with the token.")
    token: str = Field(..., description="The token string.")
