import hashlib
from dataclasses import dataclass

from app.core.config import settings
from app.core.security import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)

ACCESS_TOKEN_MAX_AGE_SECONDS = settings.jwt_access_expire_minutes * 60
REFRESH_TOKEN_MAX_AGE_SECONDS = settings.jwt_refresh_expire_days * 24 * 60 * 60


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    refresh_token_hash: str


def hash_refresh_token(token: str) -> str:
    """Refresh tokens are high-entropy random values, so a fast SHA-256
    digest is sufficient for at-rest comparison (unlike low-entropy
    passwords, which require bcrypt)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def issue_token_pair(user_id: str, role: str) -> TokenPair:
    access_token = create_access_token(user_id=user_id, role=role)
    refresh_token = create_refresh_token(user_id=user_id)
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        refresh_token_hash=hash_refresh_token(refresh_token),
    )


def decode_access(token: str) -> dict:
    return decode_access_token(token)


def decode_refresh(token: str) -> dict:
    return decode_refresh_token(token)


__all__ = [
    "TokenError",
    "TokenPair",
    "ACCESS_TOKEN_MAX_AGE_SECONDS",
    "REFRESH_TOKEN_MAX_AGE_SECONDS",
    "hash_refresh_token",
    "issue_token_pair",
    "decode_access",
    "decode_refresh",
]
