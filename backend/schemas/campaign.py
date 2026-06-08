"""Campaign schemas."""

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from models.campaign import CampaignStatus


class CampaignCreate(BaseModel):
    seed_domain: str = Field(..., description="The seed domain to find lookalikes for (e.g., acme.com)")
    email_template: Optional[str] = Field(None, description="Custom HTML template for emails")


class CampaignStatusResponse(BaseModel):
    id: UUID
    status: CampaignStatus
    metrics: Dict[str, Any]
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class CampaignResponse(CampaignStatusResponse):
    seed_domain: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
