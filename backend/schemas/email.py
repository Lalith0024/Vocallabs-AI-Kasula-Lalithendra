"""Email schemas."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from models.email_record import EmailStatus


class EmailResponse(BaseModel):
    id: UUID
    contact_id: UUID
    campaign_id: UUID
    email_address: str
    verified: bool
    confidence: Optional[float]
    status: EmailStatus
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    opened_at: Optional[datetime]
    clicked_at: Optional[datetime]
    bounced_at: Optional[datetime]

    class Config:
        from_attributes = True
