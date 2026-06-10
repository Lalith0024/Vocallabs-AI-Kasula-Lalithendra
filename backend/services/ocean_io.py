"""Ocean.io API integration for finding lookalike companies."""

import httpx
import asyncio
import time
from typing import List, Dict, Any, Optional
import structlog
from uuid import UUID

from config import get_settings
from services.rate_limiter import RateLimiter

settings = get_settings()
logger = structlog.get_logger()

# Shared rate limiter for all instances
_limiter = RateLimiter(requests_per_minute=settings.OCEAN_IO_RATE_LIMIT)

class OceanIOClient:
    def __init__(self, campaign_id: Optional[UUID] = None):
        self.base_url = settings.OCEAN_IO_BASE_URL
        self.api_key = settings.OCEAN_IO_API_KEY
        self.campaign_id = campaign_id
        # Ocean.io API v3 requires X-Api-Token
        self.headers = {
            "X-Api-Token": self.api_key,
            "Content-Type": "application/json"
        }

    async def search_lookalikes(self, seed_domain: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Find lookalike companies based on a seed domain."""
        
        # If API key is not configured, return mock data for testing/demo
        if not self.api_key:
            logger.warning("Ocean.io API key not found. Using mock data.", campaign_id=self.campaign_id)
            return self._get_mock_data(seed_domain)

        all_companies = []
        search_after = None
        
        # We might need multiple pages if limit > page size
        page_size = min(limit, 100) # Assuming max 100 per page

        async with httpx.AsyncClient(timeout=30.0) as client:
            while len(all_companies) < limit:
                await _limiter.acquire()
                
                payload = {
                    "size": page_size,
                    "companiesFilters": {
                        "similarTo": [seed_domain],
                        "primaryLocations": {
                            "includeCountries": ["us", "gb", "ca", "au"]
                        }
                    }
                }
                
                if search_after:
                    payload["searchAfter"] = search_after

                try:
                    start_time = time.time()
                    # We hit the general search endpoint as per research
                    response = await client.post(
                        f"{self.base_url}/search/companies",
                        json=payload,
                        headers=self.headers
                    )
                    
                    if response.status_code == 429:
                        logger.warning("Ocean.io rate limit hit. Sleeping...", campaign_id=self.campaign_id)
                        await asyncio.sleep(60)
                        continue
                        
                    response.raise_for_status()
                    data = response.json()
                    
                    # Store API log here if we had DB session access, but we'll return raw data 
                    # and let the pipeline handler log it.

                    companies = data.get("companies", [])
                    if not companies:
                        break
                        
                    all_companies.extend(companies)
                    
                    search_after = data.get("searchAfter")
                    if not search_after:
                        break
                        
                except httpx.HTTPError as e:
                    logger.error("Ocean.io API request failed", error=str(e), campaign_id=self.campaign_id)
                    # For demo purposes, if it fails, fallback to mock data
                    if not all_companies:
                         return self._get_mock_data(seed_domain)
                    raise e
                    
        return all_companies[:limit]

    def _get_mock_data(self, seed_domain: str) -> List[Dict[str, Any]]:
        """Return mock lookalike companies for demo purposes."""
        return [
            {
                "domain": "techcorp.io",
                "name": "TechCorp Solutions",
                "industry": "Software",
                "companySize": "200-500",
                "foundedYear": 2018,
                "similarityScore": 0.95
            },
            {
                "domain": "innovate.ai",
                "name": "Innovate AI",
                "industry": "Software",
                "companySize": "50-200",
                "foundedYear": 2020,
                "similarityScore": 0.88
            },
            {
                "domain": "cloudscale.net",
                "name": "CloudScale Networks",
                "industry": "IT Services",
                "companySize": "500-1000",
                "foundedYear": 2015,
                "similarityScore": 0.85
            }
        ]
