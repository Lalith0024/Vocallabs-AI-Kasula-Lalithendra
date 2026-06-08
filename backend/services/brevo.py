"""Brevo API integration for sending personalized emails."""

import httpx
import asyncio
from typing import Dict, Any, List, Optional
import structlog
from uuid import UUID

from config import get_settings
from services.rate_limiter import RateLimiter

settings = get_settings()
logger = structlog.get_logger()

_limiter = RateLimiter(requests_per_minute=settings.BREVO_RATE_LIMIT)

class BrevoClient:
    def __init__(self, campaign_id: Optional[UUID] = None):
        self.base_url = settings.BREVO_BASE_URL
        self.api_key = settings.BREVO_API_KEY
        self.campaign_id = campaign_id
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

    async def send_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send an email using Brevo API v3."""
        
        if not self.api_key:
            # Mock successful send
            logger.info("Brevo API key missing. Mocking email send.", to=email_data.get("to"))
            return {"messageId": f"<mock_{hash(str(email_data))}@mock-relay.brevo.com>"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            await _limiter.acquire()
            
            try:
                response = await client.post(
                    f"{self.base_url}/smtp/email",
                    json=email_data,
                    headers=self.headers
                )
                
                if response.status_code == 429:
                    logger.warning("Brevo rate limit hit. Sleeping...")
                    await asyncio.sleep(60)
                    response.raise_for_status()
                    
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                logger.error("Brevo API request failed", error=str(e))
                raise e
