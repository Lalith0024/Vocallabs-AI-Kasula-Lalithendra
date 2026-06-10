"""Pipeline orchestrator — runs all 4 stages as async tasks in FastAPI's event loop."""

import asyncio
import structlog
from datetime import datetime, timezone
from uuid import UUID
from typing import Optional, Dict, Any

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


async def _update_campaign_status(
    campaign_id: UUID,
    status: CampaignStatus,
    metrics_update: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
):
    """Update campaign status in a fresh DB session."""
    async with AsyncSessionLocal() as db:
        campaign = await db.get(Campaign, campaign_id)
        if not campaign:
            return

        campaign.status = status.value  # type: ignore

        if status == CampaignStatus.RUNNING:
            campaign.started_at = datetime.now(timezone.utc)  # type: ignore
        elif status in (CampaignStatus.COMPLETED, CampaignStatus.FAILED):
            campaign.completed_at = datetime.now(timezone.utc)  # type: ignore

        if error:
            campaign.error_message = error  # type: ignore

        if metrics_update:
            current_metrics = dict(campaign.metrics or {})  # type: ignore
            current_metrics.update(metrics_update)
            campaign.metrics = current_metrics  # type: ignore

        await db.commit()


async def _stage_1_ocean_io(campaign_id: UUID) -> int:
    """Stage 1: Find lookalike companies via Ocean.io."""
    await _update_campaign_status(campaign_id, CampaignStatus.STAGE_1)
    logger.info("Stage 1 starting", campaign_id=str(campaign_id))

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select

        campaign = await db.get(Campaign, campaign_id)
        if not campaign:
            raise ValueError("Campaign not found")

        client = OceanIOClient(campaign_id=campaign_id)
        lookalikes = await client.search_lookalikes(str(campaign.seed_domain))

        # Deduplicate
        existing_res = await db.execute(
            select(Company.domain).where(Company.campaign_id == campaign_id)
        )
        existing_domains = set(existing_res.scalars().all())

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
                ocean_io_metadata=data,
            )
            db.add(company)
            existing_domains.add(domain)
            companies_added += 1

        await db.commit()

    await _update_campaign_status(
        campaign_id,
        CampaignStatus.STAGE_1,
        metrics_update={"companies_found": companies_added},
    )
    logger.info("Stage 1 complete", companies_found=companies_added)
    return companies_added


async def _stage_2_prospeo(campaign_id: UUID) -> int:
    """Stage 2: Extract decision-makers via Prospeo."""
    await _update_campaign_status(campaign_id, CampaignStatus.STAGE_2)
    logger.info("Stage 2 starting", campaign_id=str(campaign_id))

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select

        result = await db.execute(
            select(Company).where(Company.campaign_id == campaign_id)
        )
        companies = result.scalars().all()

        existing_res = await db.execute(
            select(Contact.linkedin_url).where(Contact.campaign_id == campaign_id)
        )
        existing_urls = set(u for u in existing_res.scalars().all() if u)

        client = ProspeoClient(campaign_id=campaign_id)
        contacts_added = 0

        for company in companies:
            try:
                prospects = await client.search_prospects(str(company.domain))
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
                        prospeo_metadata=p,
                    )
                    db.add(contact)
                    if linkedin_url:
                        existing_urls.add(linkedin_url)
                    contacts_added += 1
            except Exception as e:
                logger.warning("Prospeo failed for domain", domain=company.domain, error=str(e))
                continue

        await db.commit()

    await _update_campaign_status(
        campaign_id,
        CampaignStatus.STAGE_2,
        metrics_update={"contacts_found": contacts_added},
    )
    logger.info("Stage 2 complete", contacts_found=contacts_added)
    return contacts_added


async def _stage_3_eazyreach(campaign_id: UUID) -> int:
    """Stage 3: Resolve LinkedIn URLs to verified emails via Eazyreach/Prospeo."""
    await _update_campaign_status(campaign_id, CampaignStatus.STAGE_3)
    logger.info("Stage 3 starting", campaign_id=str(campaign_id))

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        result = await db.execute(
            select(Contact)
            .where(Contact.campaign_id == campaign_id)
            .options(selectinload(Contact.company))
        )
        contacts = result.scalars().all()

        existing_res = await db.execute(
            select(EmailRecord.email_address).where(EmailRecord.campaign_id == campaign_id)
        )
        existing_emails = set(existing_res.scalars().all())

        client = EazyreachClient(campaign_id=campaign_id)
        emails_resolved = 0

        for contact in contacts:
            if not contact.linkedin_url:
                continue
            try:
                res = await client.resolve_email(
                    str(contact.linkedin_url), str(contact.company.domain)
                )
                email_addr = res.get("email", "")
                confidence = res.get("confidence", 0.0)

                # Validate email format before saving
                if (
                    email_addr
                    and confidence >= settings.EMAIL_CONFIDENCE_THRESHOLD
                    and client.is_valid_email(email_addr)
                    and email_addr not in existing_emails
                ):
                    record = EmailRecord(
                        contact_id=contact.id,
                        campaign_id=campaign_id,
                        email_address=email_addr,
                        verified=res.get("verified", False),
                        confidence=confidence,
                        eazyreach_metadata=res,
                        status=EmailStatus.PENDING.value,
                    )
                    db.add(record)
                    existing_emails.add(email_addr)
                    emails_resolved += 1
            except Exception as e:
                logger.warning(
                    "Failed to resolve email",
                    linkedin_url=contact.linkedin_url,
                    error=str(e),
                )

        await db.commit()

    # Stop here — user must approve before Stage 4
    await _update_campaign_status(
        campaign_id,
        CampaignStatus.PENDING_APPROVAL,
        metrics_update={"emails_resolved": emails_resolved},
    )
    logger.info("Stage 3 complete — awaiting approval", emails_resolved=emails_resolved)
    return emails_resolved


async def stage_4_brevo(campaign_id_str: str):
    """Stage 4: Send personalized emails via Brevo. Called after user approves."""
    campaign_id = UUID(campaign_id_str)
    await _update_campaign_status(campaign_id, CampaignStatus.STAGE_4)
    logger.info("Stage 4 starting", campaign_id=campaign_id_str)

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        campaign = await db.get(Campaign, campaign_id)
        if not campaign:
            logger.error("Campaign not found for Stage 4", campaign_id=campaign_id_str)
            return

        template = campaign.email_template

        result = await db.execute(
            select(EmailRecord)
            .where(EmailRecord.campaign_id == campaign_id)
            .where(EmailRecord.status == EmailStatus.PENDING.value)
            .options(selectinload(EmailRecord.contact).selectinload(Contact.company))
            .limit(20)  # Hard cap: max 20 emails per campaign
        )
        emails = result.scalars().all()

        client = BrevoClient(campaign_id=campaign_id)
        emails_sent = 0
        emails_failed = 0

        for email in emails:
            contact = email.contact
            company = contact.company

            context = {
                "first_name": contact.first_name or "there",
                "last_name": contact.last_name or "",
                "company_name": company.company_name or company.domain,
                "title": contact.title or "",
                "industry": company.industry or "your",
                "seed_domain": campaign.seed_domain,
            }

            html_content = generate_personalized_email(str(template), context)
            subject = f"Partnership Opportunity - {context['company_name']} & {campaign.seed_domain}"

            payload = {
                "sender": {
                    "name": settings.SENDER_NAME,
                    "email": settings.SENDER_EMAIL,
                },
                "to": [{"email": email.email_address, "name": contact.full_name}],
                "subject": subject,
                "htmlContent": html_content,
                "tags": [str(campaign_id)],
                "headers": {
                    "X-Campaign-ID": str(campaign_id),
                    "X-Email-ID": str(email.id),
                },
            }

            try:
                res = await client.send_email(payload)
                email.brevo_message_id = res.get("messageId")  # type: ignore
                email.status = EmailStatus.SENT.value  # type: ignore
                email.sent_at = datetime.now(timezone.utc)  # type: ignore
                emails_sent += 1
            except Exception as e:
                logger.error(
                    "Failed to send email",
                    to=email.email_address,
                    error=str(e),
                )
                email.status = EmailStatus.FAILED.value  # type: ignore
                email.error_message = str(e)  # type: ignore
                emails_failed += 1

        await db.commit()

    await _update_campaign_status(
        campaign_id,
        CampaignStatus.COMPLETED,
        metrics_update={"emails_sent": emails_sent, "emails_failed": emails_failed},
    )
    logger.info(
        "Stage 4 complete",
        emails_sent=emails_sent,
        emails_failed=emails_failed,
    )


async def execute_pipeline(campaign_id_str: str):
    """
    Main pipeline orchestrator.
    Runs Stages 1-3 sequentially. Stops at PENDING_APPROVAL for user to approve Stage 4.
    Called directly via asyncio.create_task() from FastAPI — no Celery needed.
    """
    campaign_id = UUID(campaign_id_str)
    logger.info("Pipeline starting", campaign_id=campaign_id_str)

    await _update_campaign_status(campaign_id, CampaignStatus.RUNNING)

    try:
        await _stage_1_ocean_io(campaign_id)
        await _stage_2_prospeo(campaign_id)
        await _stage_3_eazyreach(campaign_id)
        # Pipeline pauses here — user approval triggers stage_4_brevo separately
        logger.info("Pipeline stages 1-3 complete. Awaiting approval.", campaign_id=campaign_id_str)

    except Exception as e:
        logger.error("Pipeline failed", error=str(e), campaign_id=campaign_id_str, exc_info=True)
        await _update_campaign_status(
            campaign_id,
            CampaignStatus.FAILED,
            error=f"Pipeline failed: {str(e)}",
        )
