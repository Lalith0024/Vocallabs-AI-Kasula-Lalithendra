"""Token bucket rate limiter for API calls."""

import asyncio
import time
import random
from typing import Optional


class RateLimiter:
    """Async token bucket rate limiter."""

    def __init__(self, requests_per_minute: int, burst_size: Optional[int] = None):
        self.rate = requests_per_minute / 60.0  # Tokens per second
        self.capacity = burst_size if burst_size is not None else max(1, int(self.rate * 2))
        self.tokens = float(self.capacity)
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1):
        """Wait until enough tokens are available."""
        while True:
            async with self._lock:
                now = time.monotonic()
                # Replenish tokens
                elapsed = now - self.last_update
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                self.last_update = now

                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return

            # Not enough tokens; calculate wait time + small jitter
            wait_time = (tokens - self.tokens) / self.rate
            jitter = random.uniform(0.01, 0.1)
            await asyncio.sleep(wait_time + jitter)
