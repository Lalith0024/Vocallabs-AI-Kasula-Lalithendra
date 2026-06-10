"""Campaign endpoints including pipeline triggering and WebSocket status."""

import asyncio
from typing import List, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

import structlog
from database import get_db, AsyncSessionLocal
from models.campaign import Campaign, CampaignStatus
from models.company import Company
from models.contact import Contact
from models.email_record import EmailRecord
from schemas.campaign import CampaignCreate, CampaignResponse, CampaignStatusResponse
from schemas.company import CompanyResponse
from schemas.contact import ContactResponse
from schemas.email import EmailResponse
from jobs.pipeline import execute_pipeline, stage_4_brevo

logger = structlog.get_logger()

router = APIRouter()

# Simple connected clients manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, campaign_id: UUID):
        await websocket.accept()
        if campaign_id not in self.active_connections:
            self.active_connections[campaign_id] = []
        self.active_connections[campaign_id].append(websocket)

    def disconnect(self, websocket: WebSocket, campaign_id: UUID):
        if campaign_id in self.active_connections:
            if websocket in self.active_connections[campaign_id]:
                self.active_connections[campaign_id].remove(websocket)
            if not self.active_connections[campaign_id]:
                del self.active_connections[campaign_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

manager = ConnectionManager()

@router.post("/", response_model=CampaignResponse)
async def create_campaign(campaign_in: CampaignCreate, db: AsyncSession = Depends(get_db)):
    """Create a new campaign and trigger the pipeline."""
    # Basic domain validation
    if "." not in campaign_in.seed_domain:
        raise HTTPException(status_code=400, detail="Invalid domain format")
        
    campaign = Campaign(
        seed_domain=campaign_in.seed_domain,
        email_template=campaign_in.email_template,
        status=CampaignStatus.PENDING.value
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    
    # Trigger Celery pipeline
    execute_pipeline.delay(str(campaign.id))
    
    return campaign

@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(db: AsyncSession = Depends(get_db)):
    """List all campaigns."""
    result = await db.execute(select(Campaign).order_by(Campaign.created_at.desc()))
    return result.scalars().all()

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get full campaign details."""
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.get("/{campaign_id}/status", response_model=CampaignStatusResponse)
async def get_campaign_status(campaign_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get just the status and metrics for polling."""
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.post("/{campaign_id}/approve-send")
async def approve_campaign_send(campaign_id: UUID, db: AsyncSession = Depends(get_db)):
    """Approve a campaign that is pending_approval to send emails."""
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    if campaign.status != CampaignStatus.PENDING_APPROVAL.value:
        raise HTTPException(
            status_code=400, 
            detail=f"Campaign is in status {campaign.status}, expected {CampaignStatus.PENDING_APPROVAL.value}"
        )
        
    # Trigger Stage 4
    stage_4_brevo.delay(str(campaign_id))
    
    campaign.status = CampaignStatus.STAGE_4.value
    await db.commit()
    
    return {"status": "sending_initiated"}

# Sub-resources for detail view
@router.get("/{campaign_id}/companies", response_model=List[CompanyResponse])
async def get_campaign_companies(campaign_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.campaign_id == campaign_id))
    return result.scalars().all()

@router.get("/{campaign_id}/contacts", response_model=List[ContactResponse])
async def get_campaign_contacts(campaign_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Contact)
        .where(Contact.campaign_id == campaign_id)
        .options(selectinload(Contact.company))
    )
    return result.scalars().all()

@router.get("/{campaign_id}/emails", response_model=List[EmailResponse])
async def get_campaign_emails(campaign_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EmailRecord).where(EmailRecord.campaign_id == campaign_id))
    return result.scalars().all()


@router.websocket("/ws/{campaign_id}")
async def websocket_endpoint(websocket: WebSocket, campaign_id: UUID):
    """WebSocket for real-time campaign status updates."""
    await manager.connect(websocket, campaign_id)
    try:
        # Polling loop within the websocket connection
        # In a more advanced setup, we'd use Redis Pub/Sub to trigger updates,
        # but polling the DB every 2 seconds is fine for this assignment scale.
        while True:
            # Re-fetch from DB using fresh session each time
            # This avoids connection pool leaks and session/transaction caching issues.
            async with AsyncSessionLocal() as db:
                campaign = await db.get(Campaign, campaign_id)
                if campaign:
                    await manager.send_personal_message(
                        {
                            "status": campaign.status,
                            "metrics": campaign.metrics or {},
                            "error_message": campaign.error_message
                        }, 
                        websocket
                    )
                    
                    if campaign.status in (CampaignStatus.COMPLETED.value, CampaignStatus.FAILED.value):
                        break  # Stop polling — campaign is done
            
            await asyncio.sleep(2)
            
        try:
            await websocket.close()
        except Exception:
            pass
        manager.disconnect(websocket, campaign_id)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, campaign_id)
    except Exception as e:
        logger.error("WebSocket connection encountered an error", error=str(e), campaign_id=campaign_id, exc_info=True)
        manager.disconnect(websocket, campaign_id)
