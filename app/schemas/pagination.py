from typing import Optional
from pydantic import BaseModel


class PaginationLinks(BaseModel):
    """
    Schema for pagination links.

    Attributes:
        next (Optional[str]): The URL to the next page of results, if available. Default is None.
        previous (Optional[str]): The URL to the previous page of results, if available. Default is None.
    """

    next: Optional[str] = None
    previous: Optional[str] = None
