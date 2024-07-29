from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.pagination import PaginationLinks


class CompanyBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    name: str
    description: str
    owner_id: int
    is_visible: bool


class CompanyCreate(BaseModel):
    name: str
    description: str
    owner_id: int
    is_visible: bool


class CompanyDetail(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str
    description: str


class CompaniesListResponse(BaseModel):
    links: PaginationLinks
    companies: List[CompanyBase]
    total: int
