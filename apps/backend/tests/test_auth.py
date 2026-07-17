from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)
from app.services.token_service import hash_refresh_token
from app.utils.password import hash_password, verify_password


def test_password_hash_and_verify() -> None:
    password = "SuperSecret123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_access_token_roundtrip() -> None:
    token = create_access_token(user_id="11111111-1111-1111-1111-111111111111", role="ADMIN")
    payload = decode_access_token(token)

    assert payload["sub"] == "11111111-1111-1111-1111-111111111111"
    assert payload["role"] == "ADMIN"
    assert payload["type"] == "access"


def test_refresh_token_roundtrip_and_hash_is_deterministic() -> None:
    token = create_refresh_token(user_id="22222222-2222-2222-2222-222222222222")
    payload = decode_refresh_token(token)

    assert payload["sub"] == "22222222-2222-2222-2222-222222222222"
    assert payload["type"] == "refresh"
    assert hash_refresh_token(token) == hash_refresh_token(token)
