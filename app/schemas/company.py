from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class CompanyBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    name: str
    description: str
    owner_id: int
    is_visible: bool
    created_at: datetime
    updated_at: datetime


class CompanyCreate(BaseModel):
    name: str
    description: str
    owner_id: int
    is_visible: bool
    created_at: datetime
    updated_at: datetime


class CompanyDetail(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str
    description: str


class CompaniesListResponse(BaseModel):
    companies: List[CompanyBase]
    total: int
