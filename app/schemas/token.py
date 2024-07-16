from datetime import datetime

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    expiration: datetime


class TokenData(BaseModel):
    token: str
    email: str
