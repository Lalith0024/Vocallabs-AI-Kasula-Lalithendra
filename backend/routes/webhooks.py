"""Webhook endpoints for external services (e.g., Brevo delivery events)."""

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import structlog

from database import get_db
from models.email_record import EmailRecord, EmailStatus

logger = structlog.get_logger()
router = APIRouter()

@router.post("/brevo")
async def brevo_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Brevo transactional email webhooks (delivery, opens, clicks, bounces)."""
    
    # In production, we should validate the Brevo webhook signature here
    payload = await request.json()
    logger.info("Received Brevo webhook", payload=payload)
    
    event = payload.get("event")
    message_id = payload.get("message-id")
    
    if not message_id:
        return {"status": "ignored", "reason": "no message-id"}
        
    # Find the email record
    result = await db.execute(select(EmailRecord).where(EmailRecord.brevo_message_id == message_id))
    email_record = result.scalars().first()
    
    if not email_record:
        logger.warning(f"Webhook received for unknown message_id: {message_id}")
        return {"status": "ignored", "reason": "unknown message-id"}
        
    # Update status based on event type
    now = datetime.utcnow()
    
    if event == "delivered":
        email_record.status = EmailStatus.DELIVERED.value
        email_record.delivered_at = now
    elif event == "opened":
        # Don't overwrite if it was clicked
        if email_record.status not in (EmailStatus.CLICKED.value, EmailStatus.BOUNCED.value):
            email_record.status = EmailStatus.OPENED.value
        email_record.opened_at = now
    elif event == "click":
        email_record.status = EmailStatus.CLICKED.value
        email_record.clicked_at = now
    elif event in ("bounced", "hard_bounce", "soft_bounce", "spam", "invalid_email"):
        email_record.status = EmailStatus.BOUNCED.value
        email_record.bounced_at = now
        email_record.error_message = payload.get("reason", event)
        
    await db.commit()
    
    return {"status": "success"}
