"""Pipeline orchestrator for the 4-stage cold outreach process."""

import asyncio
import structlog
from datetime import datetime
from uuid import UUID

from celery_app import celery
from database import AsyncSessionLocal
from models.campaign import Campaign, CampaignStatus
from models.company import Company
from models.contact import Contact
from models.email_record import EmailRecord, EmailStatus

from services.ocean_io import OceanIOClient
from services.prospeo import ProspeoClient
from services.eazyreach import EazyreachClient
from services.brevo import BrevoClient
from services.email_personalization import generate_personalized_email
from config import get_settings

logger = structlog.get_logger()
settings = get_settings()

def sync_db_call(coro):
    """Helper to run async DB/Service calls in Celery's sync workers."""
    return asyncio.run(coro)

async def _update_campaign_status(campaign_id: UUID, status: CampaignStatus, metrics_update: dict = None, error: str = None):
    async with AsyncSessionLocal() as db:
        campaign = await db.get(Campaign, campaign_id)
        if not campaign:
            return
            
        campaign.status = status.value
        if status == CampaignStatus.RUNNING:
            campaign.started_at = datetime.utcnow()
        elif status in (CampaignStatus.COMPLETED, CampaignStatus.FAILED):
            campaign.completed_at = datetime.utcnow()
            
        if error:
            campaign.error_message = error
            
        if metrics_update:
            current_metrics = dict(campaign.metrics or {})
            current_metrics.update(metrics_update)
            campaign.metrics = current_metrics
            
        await db.commit()

# --- Stage 1: Ocean.io ---
@celery.task(bind=True, max_retries=3)
def stage_1_ocean_io(self, campaign_id_str: str):
    """Find lookalike companies."""
    campaign_id = UUID(campaign_id_str)
    
    async def _run():
        await _update_campaign_status(campaign_id, CampaignStatus.STAGE_1)
        try:
            async with AsyncSessionLocal() as db:
                from sqlalchemy import select
                campaign = await db.get(Campaign, campaign_id)
                if not campaign:
                    return {"error": "Campaign not found"}
                    
                client = OceanIOClient(campaign_id=campaign_id)
                lookalikes = await client.search_lookalikes(campaign.seed_domain)
                
                # Get existing domains to avoid duplicate constraint violations
                existing_domains_res = await db.execute(
                    select(Company.domain).where(Company.campaign_id == campaign_id)
                )
                existing_domains = set(existing_domains_res.scalars().all())

                # Store companies
                companies_added = 0
                for data in lookalikes:
                    domain = data.get("domain")
                    if not domain or domain in existing_domains:
                        continue
                    company = Company(
                        campaign_id=campaign_id,
                        domain=domain,
                        company_name=data.get("name"),
                        industry=data.get("industry"),
                        similarity_score=data.get("similarityScore"),
                        ocean_io_metadata=data
                    )
                    db.add(company)
                    existing_domains.add(domain)
                    companies_added += 1
                    
                await db.commit()
                
                # Update metrics
                await _update_campaign_status(
                    campaign_id, 
                    CampaignStatus.STAGE_1,
                    metrics_update={"companies_found": companies_added}
                )
                
                return {"campaign_id": str(campaign_id), "companies_found": companies_added}
        except Exception as e:
            logger.error("Stage 1 failed", error=str(e), exc_info=True)
            if self.request.retries >= self.max_retries:
                await _update_campaign_status(campaign_id, CampaignStatus.FAILED, error=f"Stage 1 failed: {str(e)}")
            raise self.retry(exc=e, countdown=60)
                
    return sync_db_call(_run())

# --- Stage 2: Prospeo ---
@celery.task(bind=True, max_retries=3)
def stage_2_prospeo(self, stage_1_result, campaign_id_str: str):
    """Extract decision makers from companies."""
    campaign_id = UUID(campaign_id_str)
    
    async def _run():
        await _update_campaign_status(campaign_id, CampaignStatus.STAGE_2)
        try:
            async with AsyncSessionLocal() as db:
                from sqlalchemy import select
                campaign = await db.get(Campaign, campaign_id)
                if not campaign:
                    return {"error": "Campaign not found"}
                    
                result = await db.execute(select(Company).where(Company.campaign_id == campaign_id))
                companies = result.scalars().all()
                
                client = ProspeoClient(campaign_id=campaign_id)
                
                # Get existing linkedin URLs to avoid duplicate constraint violations
                existing_urls_res = await db.execute(
                    select(Contact.linkedin_url).where(Contact.campaign_id == campaign_id)
                )
                existing_urls = set(url for url in existing_urls_res.scalars().all() if url)
                
                contacts_added = 0
                for company in companies:
                    try:
                        prospects = await client.search_prospects(company.domain)
                        for p in prospects:
                            linkedin_url = p.get("linkedin_url")
                            if linkedin_url and linkedin_url in existing_urls:
                                continue
                            contact = Contact(
                                company_id=company.id,
                                campaign_id=campaign_id,
                                first_name=p.get("first_name"),
                                last_name=p.get("last_name"),
                                title=p.get("job_title"),
                                linkedin_url=linkedin_url,
                                prospeo_metadata=p
                            )
                            db.add(contact)
                            if linkedin_url:
                                existing_urls.add(linkedin_url)
                            contacts_added += 1
                            
                    except Exception as e:
                        logger.warning(f"Failed to extract contacts for {company.domain}", error=str(e))
                        continue # Try next company instead of failing whole stage
                
                await db.commit()
                
                await _update_campaign_status(
                    campaign_id, 
                    CampaignStatus.STAGE_2,
                    metrics_update={"contacts_found": contacts_added}
                )
                
                return {"campaign_id": str(campaign_id), "contacts_found": contacts_added}
        except Exception as e:
            logger.error("Stage 2 failed", error=str(e), exc_info=True)
            if self.request.retries >= self.max_retries:
                await _update_campaign_status(campaign_id, CampaignStatus.FAILED, error=f"Stage 2 failed: {str(e)}")
            raise self.retry(exc=e, countdown=60)
            
    return sync_db_call(_run())

# --- Stage 3: Eazyreach ---
@celery.task(bind=True, max_retries=3)
def stage_3_eazyreach(self, stage_2_result, campaign_id_str: str):
    """Resolve emails from LinkedIn URLs."""
    campaign_id = UUID(campaign_id_str)
    
    async def _run():
        await _update_campaign_status(campaign_id, CampaignStatus.STAGE_3)
        try:
            async with AsyncSessionLocal() as db:
                from sqlalchemy import select
                from sqlalchemy.orm import selectinload
                
                campaign = await db.get(Campaign, campaign_id)
                if not campaign:
                    return {"error": "Campaign not found"}
                    
                result = await db.execute(
                    select(Contact)
                    .where(Contact.campaign_id == campaign_id)
                    .options(selectinload(Contact.company))
                )
                contacts = result.scalars().all()
                
                client = EazyreachClient(campaign_id=campaign_id)
                
                # Get existing emails to avoid duplicates
                existing_emails_res = await db.execute(
                    select(EmailRecord.email_address).where(EmailRecord.campaign_id == campaign_id)
                )
                existing_emails = set(email_addr for email_addr in existing_emails_res.scalars().all())
                
                emails_resolved = 0
                for contact in contacts:
                    if not contact.linkedin_url:
                        continue
                        
                    try:
                        res = await client.resolve_email(contact.linkedin_url, contact.company.domain)
                        email_addr = res.get("email")
                        confidence = res.get("confidence", 0.0)
                        
                        if email_addr and confidence >= 0.7:
                            if email_addr in existing_emails:
                                continue
                            email_record = EmailRecord(
                                contact_id=contact.id,
                                campaign_id=campaign_id,
                                email_address=email_addr,
                                verified=res.get("verified", False),
                                confidence=confidence,
                                eazyreach_metadata=res,
                                status=EmailStatus.PENDING.value
                            )
                            db.add(email_record)
                            existing_emails.add(email_addr)
                            emails_resolved += 1
                            
                    except Exception as e:
                        logger.warning(f"Failed to resolve email for {contact.linkedin_url}", error=str(e))
                
                await db.commit()
                
                await _update_campaign_status(
                    campaign_id, 
                    CampaignStatus.PENDING_APPROVAL, # Stop here for safety checkpoint
                    metrics_update={"emails_resolved": emails_resolved}
                )
                
                return {"campaign_id": str(campaign_id), "emails_resolved": emails_resolved}
        except Exception as e:
            logger.error("Stage 3 failed", error=str(e), exc_info=True)
            if self.request.retries >= self.max_retries:
                await _update_campaign_status(campaign_id, CampaignStatus.FAILED, error=f"Stage 3 failed: {str(e)}")
            raise self.retry(exc=e, countdown=60)
            
    return sync_db_call(_run())


# --- Stage 4: Brevo ---
@celery.task(bind=True, max_retries=3)
def stage_4_brevo(self, campaign_id_str: str):
    """Send personalized emails. Triggered manually after approval."""
    campaign_id = UUID(campaign_id_str)
    
    async def _run():
        await _update_campaign_status(campaign_id, CampaignStatus.STAGE_4)
        try:
            async with AsyncSessionLocal() as db:
                from sqlalchemy import select
                from sqlalchemy.orm import selectinload
                
                # Get campaign template
                campaign = await db.get(Campaign, campaign_id)
                if not campaign:
                    return {"error": "Campaign not found"}
                template = campaign.email_template
                
                # Get pending emails
                result = await db.execute(
                    select(EmailRecord)
                    .where(EmailRecord.campaign_id == campaign_id)
                    .where(EmailRecord.status == EmailStatus.PENDING.value)
                    .options(selectinload(EmailRecord.contact).selectinload(Contact.company))
                )
                emails = result.scalars().all()
                
                client = BrevoClient(campaign_id=campaign_id)
                emails_sent = 0
                emails_failed = 0
                
                for email in emails:
                    contact = email.contact
                    company = contact.company
                    
                    # Context for personalization
                    context = {
                        "first_name": contact.first_name,
                        "last_name": contact.last_name,
                        "company_name": company.company_name or company.domain,
                        "title": contact.title,
                        "industry": company.industry or "your",
                        "seed_domain": campaign.seed_domain
                    }
                    
                    html_content = generate_personalized_email(template, context)
                    subject = f"Partnership Opportunity - {context['company_name']} & {campaign.seed_domain}"
                    
                    payload = {
                        "sender": {"name": settings.SENDER_NAME, "email": settings.SENDER_EMAIL},
                        "to": [{"email": email.email_address, "name": contact.full_name}],
                        "subject": subject,
                        "htmlContent": html_content,
                        "tags": [str(campaign_id)],
                        "headers": {
                            "X-Campaign-ID": str(campaign_id),
                            "X-Email-ID": str(email.id)
                        }
                    }
                    
                    try:
                        res = await client.send_email(payload)
                        email.brevo_message_id = res.get("messageId")
                        email.status = EmailStatus.SENT.value
                        email.sent_at = datetime.utcnow()
                        emails_sent += 1
                    except Exception as e:
                        logger.error(f"Failed to send email to {email.email_address}", error=str(e))
                        email.status = EmailStatus.FAILED.value
                        email.error_message = str(e)
                        emails_failed += 1
                
                await db.commit()
                
                await _update_campaign_status(
                    campaign_id, 
                    CampaignStatus.COMPLETED,
                    metrics_update={
                        "emails_sent": emails_sent,
                        "emails_failed": emails_failed
                    }
                )
                
                return {
                    "campaign_id": str(campaign_id), 
                    "emails_sent": emails_sent,
                    "emails_failed": emails_failed
                }
        except Exception as e:
            logger.error("Stage 4 failed", error=str(e), exc_info=True)
            if self.request.retries >= self.max_retries:
                await _update_campaign_status(campaign_id, CampaignStatus.FAILED, error=f"Stage 4 failed: {str(e)}")
            raise self.retry(exc=e, countdown=60)
            
    return sync_db_call(_run())

# --- Orchestrator ---
@celery.task
def execute_pipeline(campaign_id_str: str):
    """Kicks off the pipeline sequentially."""
    # Using celery chord/chain to link stages
    from celery import chain
    
    # We pass campaign_id down the chain. The results of the previous task
    # are passed as the first argument to the next task in the chain automatically.
    workflow = chain(
        stage_1_ocean_io.s(campaign_id_str),
        stage_2_prospeo.s(campaign_id_str),
        stage_3_eazyreach.s(campaign_id_str)
        # Stage 4 is intentionally omitted because it requires user approval
    )
    
    # Mark as running
    sync_db_call(_update_campaign_status(UUID(campaign_id_str), CampaignStatus.RUNNING))
    
    workflow.apply_async()
    return {"status": "started", "campaign_id": campaign_id_str}
