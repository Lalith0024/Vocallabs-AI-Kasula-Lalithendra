"""Pydantic schemas for API requests and responses."""

from schemas.campaign import CampaignCreate, CampaignResponse, CampaignStatusResponse
from schemas.company import CompanyResponse
from schemas.contact import ContactResponse
from schemas.email import EmailResponse

__all__ = [
    "CampaignCreate",
    "CampaignResponse",
    "CampaignStatusResponse",
    "CompanyResponse",
    "ContactResponse",
    "EmailResponse",
]
