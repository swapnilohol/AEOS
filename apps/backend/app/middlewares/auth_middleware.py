import logging

import redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings

logger = logging.getLogger("aeos.backend")

RATE_LIMITED_PATHS = {"/api/v1/auth/login", "/api/v1/auth/refresh"}
WINDOW_SECONDS = 60
MAX_REQUESTS_PER_WINDOW = 10

_redis_client: redis.Redis | None = None


def _get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    """Limits requests per client IP on sensitive auth endpoints."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path not in RATE_LIMITED_PATHS:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"ratelimit:auth:{request.url.path}:{client_ip}"

        try:
            client = _get_redis_client()
            current = client.incr(key)
            if current == 1:
                client.expire(key, WINDOW_SECONDS)
            if current > MAX_REQUESTS_PER_WINDOW:
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "message": "Too many requests. Please try again later.",
                        "data": None,
                        "errors": ["rate_limited"],
                    },
                )
        except redis.RedisError:
            # Fail open: never block auth entirely due to a Redis outage.
            logger.error("Rate limiter unavailable; allowing request through")

        return await call_next(request)
