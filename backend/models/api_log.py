"""ApiLog model — audit trail of all external API calls."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base


class ApiLog(Base):
    __tablename__ = "api_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    service_name = Column(String(50), nullable=False, index=True)  # ocean_io, prospeo, eazyreach, brevo
    endpoint = Column(String(500), nullable=False)
    method = Column(String(10), default="POST")
    request_payload = Column(JSON, nullable=True)
    response_payload = Column(JSON, nullable=True)
    status_code = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)  # Response time in milliseconds
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="api_logs")

    def __repr__(self):
        return f"<ApiLog {self.service_name} {self.endpoint} status={self.status_code}>"
