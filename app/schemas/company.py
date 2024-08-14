from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.pagination import PaginationLinks


class CompanyBase(BaseModel):
    """
    Base schema for a company.
    """

    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = Field(
        None, description="The unique identifier of the company. Default is None."
    )
    name: str = Field(..., description="The name of the company.")
    description: str = Field(..., description="A brief description of the company.")
    owner_id: int = Field(..., description="The ID of the owner of the company.")
    is_visible: bool = Field(
        ..., description="Flag indicating if the company is visible."
    )


class CompanyCreate(BaseModel):
    """
    Schema for creating a new company.
    """

    name: str = Field(..., description="The name of the company.")
    description: str = Field(..., description="A brief description of the company.")
    owner_id: int = Field(..., description="The ID of the owner of the company.")
    is_visible: bool = Field(
        ..., description="Flag indicating if the company is visible."
    )


class CompanyDetail(CompanyBase):
    """
    Schema for detailed view of a company.
    Inherits all attributes from CompanyBase.
    """

    pass


class CompanyUpdate(BaseModel):
    """
    Schema for updating an existing company.
    """

    name: str = Field(..., description="The updated name of the company.")
    description: str = Field(..., description="The updated description of the company.")


class CompaniesListResponse(BaseModel):
    """
    Schema for a paginated response containing a list of companies.
    """

    links: PaginationLinks = Field(
        ..., description="Pagination links for navigating through the list."
    )
    companies: List[CompanyBase] = Field(..., description="A list of companies.")
    total: int = Field(..., description="The total number of companies.")
