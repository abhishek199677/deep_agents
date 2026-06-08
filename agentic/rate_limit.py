from __future__ import annotations

import time
from collections import defaultdict

from fastapi import Request, HTTPException, status

from agentic.config import settings


class MemoryRateLimiter:
    """Simple in-memory rate limiter (replace with Redis in production)."""

    def __init__(self):
        self._buckets: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str, max_calls: int, window_seconds: int = 60) -> None:
        now = time.time()
        window_start = now - window_seconds
        self._buckets[key] = [t for t in self._buckets[key] if t > window_start]
        if len(self._buckets[key]) >= max_calls:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again later.",
            )
        self._buckets[key].append(now)


rate_limiter = MemoryRateLimiter()


async def check_rate_limit(request: Request) -> None:
    user_id = getattr(request.state, "user_id", request.client.host)
    rate_limiter.check(
        key=f"rate:{user_id}",
        max_calls=settings.rate_limit_per_minute,
        window_seconds=60,
    )
