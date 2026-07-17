import logging

import httpx

from runner.config import settings

logger = logging.getLogger("aeos.executor")


def trigger_scoring(submission_id: str) -> None:
    """Best-effort call into the backend's Scoring Module right after this
    submission's raw execution results and Score row are committed. Failure
    here does not fail the execution job — the submission stays COMPLETED
    with its raw functional score; scoring can be retried/recomputed later
    via the same internal endpoint (see Known Issues in docs/README.md)."""
    url = f"{settings.backend_internal_url}/internal/scoring/submissions/{submission_id}/calculate"
    try:
        response = httpx.post(
            url,
            headers={"X-Internal-Token": settings.internal_service_token},
            timeout=10.0,
        )
        if response.status_code >= 400:
            logger.error(
                "Scoring trigger failed for submission %s: HTTP %s", submission_id, response.status_code
            )
    except httpx.HTTPError:
        logger.exception("Scoring trigger request failed for submission %s", submission_id)
