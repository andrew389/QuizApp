from typing import Optional

from pydantic import BaseModel


class PaginationLinks(BaseModel):
    next: Optional[str] = None
    previous: Optional[str] = None
