from fastapi import Header, HTTPException, status

from app.core.config import settings


def verify_internal_token(x_internal_token: str = Header(default="")) -> None:
    """Guards service-to-service endpoints (e.g. the Executor calling back
    into the Scoring API) with a shared static token instead of user JWTs,
    since the caller isn't a logged-in user."""
    if x_internal_token != settings.internal_service_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal service token"
        )
