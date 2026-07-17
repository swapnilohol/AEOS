import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.core.config import settings


class TokenError(Exception):
    """Raised when a JWT cannot be decoded or has expired."""


def create_jwt(
    subject: str,
    secret: str,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, secret, algorithm=settings.jwt_algorithm)


def decode_jwt(token: str, secret: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise TokenError("Invalid or expired token") from exc


def create_access_token(user_id: str, role: str) -> str:
    return create_jwt(
        subject=user_id,
        secret=settings.jwt_secret,
        expires_delta=timedelta(minutes=settings.jwt_access_expire_minutes),
        extra_claims={"role": role, "type": "access"},
    )


def create_refresh_token(user_id: str) -> str:
    return create_jwt(
        subject=user_id,
        secret=settings.jwt_refresh_secret,
        expires_delta=timedelta(days=settings.jwt_refresh_expire_days),
        extra_claims={"type": "refresh"},
    )


def decode_access_token(token: str) -> dict[str, Any]:
    return decode_jwt(token, settings.jwt_secret)


def decode_refresh_token(token: str) -> dict[str, Any]:
    return decode_jwt(token, settings.jwt_refresh_secret)
