"""Campaign model — tracks the lifecycle of an outreach campaign."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
import enum


class CampaignStatus(str, enum.Enum):
    """Campaign lifecycle states."""
    PENDING = "pending"
    RUNNING = "running"
    STAGE_1 = "stage_1"          # Ocean.io — finding lookalikes
    STAGE_2 = "stage_2"          # Prospeo — extracting contacts
    STAGE_3 = "stage_3"          # Eazyreach — resolving emails
    STAGE_4 = "stage_4"          # Brevo — sending emails
    PENDING_APPROVAL = "pending_approval"  # Waiting for user to approve send
    COMPLETED = "completed"
    FAILED = "failed"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seed_domain = Column(String(255), nullable=False, index=True)
    status = Column(
        String(50),
        default=CampaignStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    email_template = Column(Text, nullable=True)

    # Aggregated metrics (updated after each stage)
    metrics = Column(JSON, default=dict, nullable=False)

    # Celery task ID for tracking
    celery_task_id = Column(String(255), nullable=True)

    # Relationships
    companies = relationship(
        "Company", back_populates="campaign", cascade="all, delete-orphan"
    )
    contacts = relationship(
        "Contact", back_populates="campaign", cascade="all, delete-orphan"
    )
    emails = relationship(
        "EmailRecord", back_populates="campaign", cascade="all, delete-orphan"
    )
    api_logs = relationship(
        "ApiLog", back_populates="campaign", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Campaign {self.id} domain={self.seed_domain} status={self.status}>"
