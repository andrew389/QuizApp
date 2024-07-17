from typing import Optional, List

from pydantic import BaseModel, ConfigDict


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
    companies: List[CompanyBase]
    total: int
