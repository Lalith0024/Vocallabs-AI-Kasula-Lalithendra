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

        all_prospects = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            await _limiter.acquire()
            
            payload = {
                "company_domain": domain,
                "person_job_title": settings.TARGET_JOB_TITLES,
                # Additional filters could be added here
            }

            try:
                # Real endpoint as per research
                response = await client.post(
                    f"{self.base_url}/company-search",
                    json=payload,
                    headers=self.headers
                )
                
                if response.status_code == 404:
                    logger.info("Domain not found in Prospeo", domain=domain)
                    return []
                    
                if response.status_code == 429:
                    logger.warning("Prospeo rate limit hit. Sleeping...")
                    await asyncio.sleep(60)
                    # We'll rely on the Celery task retry logic for 429s instead of deep nesting here
                    response.raise_for_status()
                    
                response.raise_for_status()
                data = response.json()
                
                # Prospeo returns a list of results in email_list
                prospects = data.get("response", {}).get("email_list", [])
                
                # Filter out excluded titles
                filtered_prospects = []
                for p in prospects:
                    title = p.get("job_title", "")
                    if any(excl.lower() in title.lower() for excl in settings.EXCLUDED_TITLE_KEYWORDS):
                        continue
                    filtered_prospects.append(p)
                    
                return filtered_prospects
                
            except httpx.HTTPError as e:
                logger.error("Prospeo API request failed", error=str(e), domain=domain)
                # Fallback to mock data on error for demo purposes
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
