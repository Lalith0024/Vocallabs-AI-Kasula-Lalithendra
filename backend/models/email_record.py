"""EmailRecord model — resolved emails and their delivery status."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Float, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
import enum


class EmailStatus(str, enum.Enum):
    """Email delivery lifecycle."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    BOUNCED = "bounced"
    OPENED = "opened"
    CLICKED = "clicked"
    FAILED = "failed"


class EmailRecord(Base):
    __tablename__ = "emails"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    campaign_id = Column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email_address = Column(String(320), nullable=False, index=True)
    verified = Column(Boolean, default=False)
    confidence = Column(Float, nullable=True)

    # Eazyreach raw response
    eazyreach_metadata = Column(JSON, default=dict)

    # Brevo tracking
    brevo_message_id = Column(String(500), nullable=True)
    status = Column(
        String(50),
        default=EmailStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    bounced_at = Column(DateTime, nullable=True)
    error_message = Column(String(1000), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    contact = relationship("Contact", back_populates="emails")
    campaign = relationship("Campaign", back_populates="emails")

    def __repr__(self):
        return f"<EmailRecord {self.email_address} status={self.status}>"
