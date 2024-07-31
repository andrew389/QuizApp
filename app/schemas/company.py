from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.pagination import PaginationLinks


class CompanyBase(BaseModel):
    """
    Base schema for a company.

    Attributes:
        id (Optional[int]): The unique identifier of the company. Default is None.
        name (str): The name of the company.
        description (str): A brief description of the company.
        owner_id (int): The ID of the owner of the company.
        is_visible (bool): Flag indicating if the company is visible.
    """

    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    name: str
    description: str
    owner_id: int
    is_visible: bool


class CompanyCreate(BaseModel):
    """
    Schema for creating a new company.

    Attributes:
        name (str): The name of the company.
        description (str): A brief description of the company.
        owner_id (int): The ID of the owner of the company.
        is_visible (bool): Flag indicating if the company is visible.
    """

    name: str
    description: str
    owner_id: int
    is_visible: bool


class CompanyDetail(CompanyBase):
    """
    Schema for detailed view of a company.
    Inherits all attributes from CompanyBase.
    """

    pass


class CompanyUpdate(BaseModel):
    """
    Schema for updating an existing company.

    Attributes:
        name (str): The updated name of the company.
        description (str): The updated description of the company.
    """

    name: str
    description: str


class CompaniesListResponse(BaseModel):
    """
    Schema for a paginated response containing a list of companies.

    Attributes:
        links (PaginationLinks): Pagination links for navigating through the list.
        companies (List[CompanyBase]): A list of companies.
        total (int): The total number of companies.
    """

    links: PaginationLinks
    companies: List[CompanyBase]
    total: int
