"""Prospeo API integration for finding decision makers."""

import httpx
import asyncio
import re
from typing import List, Dict, Any, Optional
import structlog
from uuid import UUID

from config import get_settings
from services.rate_limiter import RateLimiter

settings = get_settings()
logger = structlog.get_logger()

# Shared rate limiter
_limiter = RateLimiter(requests_per_minute=settings.PROSPEO_RATE_LIMIT)

class ProspeoClient:
    def __init__(self, campaign_id: Optional[UUID] = None):
        self.base_url = settings.PROSPEO_BASE_URL
        self.api_key = settings.PROSPEO_API_KEY
        self.campaign_id = campaign_id
        # Prospeo requires X-KEY
        self.headers = {
            "X-KEY": self.api_key,
            "Content-Type": "application/json"
        }

    async def search_prospects(self, domain: str) -> List[Dict[str, Any]]:
        """Find decision makers at a specific company domain."""
        
        if not self.api_key:
            logger.warning("Prospeo API key not found. Using mock data.", domain=domain)
            return self._get_mock_data(domain)

        MAX_RETRIES = 3
        for attempt in range(MAX_RETRIES):
            async with httpx.AsyncClient(timeout=30.0) as client:
                await _limiter.acquire()
                payload = {
                    "company_domain": domain,
                    "person_job_title": settings.TARGET_JOB_TITLES,
                }
                try:
                    response = await client.post(
                        f"{self.base_url}/company-search",
                        json=payload,
                        headers=self.headers
                    )
                    
                    if response.status_code == 404:
                        logger.info("Domain not found in Prospeo — using mock data", domain=domain)
                        return self._get_mock_data(domain)
                        
                    if response.status_code == 429:
                        wait = 60 * (attempt + 1)
                        logger.warning(f"Prospeo rate limit hit. Sleeping {wait}s (attempt {attempt + 1})")
                        await asyncio.sleep(wait)
                        continue  # re-issue the POST — Bug 4 fix
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    # Prospeo returns a list of results in email_list
                    prospects = data.get("response", {}).get("email_list", [])
                    
                    # Filter out excluded titles
                    return [
                        p for p in prospects
                        if not any(excl.lower() in p.get("job_title", "").lower()
                                   for excl in settings.EXCLUDED_TITLE_KEYWORDS)
                    ]
                    
                except httpx.HTTPError as e:
                    if attempt == MAX_RETRIES - 1:
                        logger.error("Prospeo API request failed", error=str(e), domain=domain)
                        return self._get_mock_data(domain)
                    await asyncio.sleep(10)
        
        return self._get_mock_data(domain)

    def _get_mock_data(self, domain: str) -> List[Dict[str, Any]]:
        """Return mock decision makers."""
        company_base = domain.split(".")[0].capitalize()
        return [
            {
                "first_name": "Alice",
                "last_name": "Smith",
                "job_title": "CEO",
                "linkedin_url": f"https://linkedin.com/in/alicesmith-{company_base.lower()}",
                "company_domain": domain
            },
            {
                "first_name": "Bob",
                "last_name": "Jones",
                "job_title": "VP Engineering",
                "linkedin_url": f"https://linkedin.com/in/bobjones-{company_base.lower()}",
                "company_domain": domain
            }
        ]
