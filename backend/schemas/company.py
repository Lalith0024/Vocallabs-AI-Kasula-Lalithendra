"""Company schemas."""

from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class CompanyResponse(BaseModel):
    id: UUID
    campaign_id: UUID
    domain: str
    company_name: Optional[str]
    industry: Optional[str]
    employee_count: Optional[int]
    founded_year: Optional[int]
    linkedin_url: Optional[str]
    similarity_score: Optional[float]
    location: Optional[str]

    class Config:
        from_attributes = True
