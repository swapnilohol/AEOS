import logging

import redis

from app.core.config import settings

logger = logging.getLogger("aeos.backend")

EXECUTION_QUEUE_KEY = "execution_queue"

_client: redis.Redis | None = None


def _get_redis_client() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(settings.redis_url, decode_responses=True)
    return _client


def enqueue_submission(submission_id: str) -> None:
    """Pushes a submission ID onto the execution queue for the Executor
    service to pick up. Best-effort: if Redis is briefly unavailable, the
    submission stays PENDING in the database and can be re-enqueued later
    rather than failing the whole submit request."""
    try:
        _get_redis_client().rpush(EXECUTION_QUEUE_KEY, submission_id)
    except redis.RedisError:
        logger.error("Failed to enqueue submission %s for execution", submission_id)
