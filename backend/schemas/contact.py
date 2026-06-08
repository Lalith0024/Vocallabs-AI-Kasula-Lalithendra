"""Contact schemas."""

from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class ContactResponse(BaseModel):
    id: UUID
    company_id: UUID
    campaign_id: UUID
    first_name: Optional[str]
    last_name: Optional[str]
    title: Optional[str]
    linkedin_url: Optional[str]
    seniority: Optional[str]
    full_name: str

    class Config:
        from_attributes = True
