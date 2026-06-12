from __future__ import annotations

import time
import logging
from collections import defaultdict

from fastapi import Request, HTTPException, status

from agentic.config import settings

logger = logging.getLogger(__name__)


class MemoryRateLimiter:
    """Simple in-memory rate limiter (fallback when Redis is unavailable)."""

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


class RedisRateLimiter:
    """Redis-backed rate limiter for production use."""

    def __init__(self, redis_url: str):
        import redis.asyncio as aioredis
        self._redis: aioredis.Redis | None = None
        self._redis_url = redis_url

    async def _get_redis(self):
        if self._redis is None:
            import redis.asyncio as aioredis
            self._redis = aioredis.from_url(
                self._redis_url,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
        return self._redis

    async def check(self, key: str, max_calls: int, window_seconds: int = 60) -> None:
        try:
            r = await self._get_redis()
            now = int(time.time())
            window_start = now - window_seconds
            pipe = r.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, window_seconds)
            results = await pipe.execute()
            count = results[1]
            if count >= max_calls:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Try again later.",
                )
        except HTTPException:
            raise
        except Exception:
            logger.warning("Redis rate limiter unavailable, falling back to memory")
            _fallback.check(key, max_calls, window_seconds)


_redis_limiter = RedisRateLimiter(settings.redis_url)
_fallback = MemoryRateLimiter()


async def check_rate_limit(request: Request) -> None:
    user_id = getattr(request.state, "user_id", request.client.host)
    key = f"rate:{user_id}"
    await _redis_limiter.check(
        key=key,
        max_calls=settings.rate_limit_per_minute,
        window_seconds=60,
    )
