from typing import Optional
from pydantic import BaseModel, Field


class PaginationLinks(BaseModel):
    """
    Schema for pagination links.
    """

    next: Optional[str] = Field(
        None,
        description="The URL to the next page of results, if available. Default is None.",
    )
    previous: Optional[str] = Field(
        None,
        description="The URL to the previous page of results, if available. Default is None.",
    )
