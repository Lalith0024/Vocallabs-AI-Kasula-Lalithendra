"""Contact model — decision-makers extracted via Prospeo."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    campaign_id = Column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    title = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    seniority = Column(String(100), nullable=True)

    # Full API response for debugging
    prospeo_metadata = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Unique per campaign (same LinkedIn profile can appear in different campaigns)
    __table_args__ = (
        UniqueConstraint(
            "campaign_id", "linkedin_url", name="uq_contact_campaign_linkedin"
        ),
    )

    # Relationships
    company = relationship("Company", back_populates="contacts")
    campaign = relationship("Campaign", back_populates="contacts")
    emails = relationship(
        "EmailRecord", back_populates="contact", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        parts = [p for p in [self.first_name, self.last_name] if p]
        return " ".join(parts) or "Unknown"

    def __repr__(self):
        return f"<Contact {self.full_name} ({self.title})>"
