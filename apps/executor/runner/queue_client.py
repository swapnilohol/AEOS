import redis

from runner.config import settings

_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(settings.redis_url, decode_responses=True)
    return _client


def dequeue_submission_id() -> str | None:
    """Blocking pop with a timeout so the worker loop can check for shutdown
    signals periodically instead of blocking forever."""
    client = get_redis_client()
    result = client.brpop([settings.execution_queue_key], timeout=settings.queue_poll_timeout_seconds)
    if result is None:
        return None
    _, submission_id = result
    return submission_id
