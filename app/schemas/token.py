from datetime import datetime

from pydantic import BaseModel, field_validator


class Token(BaseModel):
    access_token: str
    token_type: str
    expiration: float

    @field_validator("expiration", mode="before")
    def parse_expiration(cls, value):
        if isinstance(value, datetime):
            return value.timestamp()
        return value

    @field_validator("expiration", mode="after")
    def format_expiration(cls, value):
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value)
        return value


class TokenData(BaseModel):
    token: str
    email: str
