"""Company model — stores lookalike companies found via Ocean.io."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    domain = Column(String(255), nullable=False, index=True)
    company_name = Column(String(500), nullable=True)
    industry = Column(String(255), nullable=True)
    employee_count = Column(Integer, nullable=True)
    founded_year = Column(Integer, nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    similarity_score = Column(Float, nullable=True)
    location = Column(String(255), nullable=True)

    # Full API response for debugging
    ocean_io_metadata = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Unique per campaign (same domain can appear in different campaigns)
    __table_args__ = (
        UniqueConstraint("campaign_id", "domain", name="uq_company_campaign_domain"),
    )

    # Relationships
    campaign = relationship("Campaign", back_populates="companies")
    contacts = relationship(
        "Contact", back_populates="company", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Company {self.domain} ({self.company_name})>"
