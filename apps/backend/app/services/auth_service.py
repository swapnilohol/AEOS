import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import RoleName, User
from app.repositories.user_repository import UserRepository
from app.services.activity_service import ActivityService
from app.services.token_service import (
    REFRESH_TOKEN_MAX_AGE_SECONDS,
    TokenError,
    TokenPair,
    decode_refresh,
    hash_refresh_token,
    issue_token_pair,
)
from app.utils.password import hash_password, verify_password


class InvalidCredentialsError(Exception):
    """Generic auth failure. Message is intentionally non-specific."""


class AccountLockedError(Exception):
    pass


class AccountInactiveError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class EmailAlreadyExistsError(Exception):
    pass


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)

    def login(self, email: str, password: str) -> tuple[TokenPair, User]:
        user = self.repo.get_by_email(email)

        if user is None:
            # Perform a dummy hash check to keep response timing consistent
            # and avoid leaking whether the email exists.
            verify_password(password, "$2b$12$" + "x" * 53)
            raise InvalidCredentialsError()

        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise AccountLockedError()

        if not verify_password(password, user.password_hash):
            self.repo.record_failed_login(
                user, settings.login_max_attempts, settings.login_lockout_minutes
            )
            self.repo.commit()
            raise InvalidCredentialsError()

        if not user.is_active:
            raise AccountInactiveError()

        self.repo.record_successful_login(user)
        token_pair = issue_token_pair(user_id=str(user.id), role=user.role.name)
        self.repo.set_refresh_token_hash(user, token_pair.refresh_token_hash)
        self.repo.commit()
        self.repo.refresh(user)
        ActivityService(self.db).log(user.id, "LOGIN")

        return token_pair, user

    def refresh(self, refresh_token: str) -> tuple[TokenPair, User]:
        try:
            payload = decode_refresh(refresh_token)
        except TokenError as exc:
            raise InvalidTokenError() from exc

        try:
            user_id = uuid.UUID(payload["sub"])
        except (ValueError, KeyError) as exc:
            raise InvalidTokenError() from exc

        user = self.repo.get_by_id(user_id)
        if user is None or not user.is_active:
            raise InvalidTokenError()

        if user.refresh_token_hash != hash_refresh_token(refresh_token):
            # Token reuse or stale token: revoke session defensively.
            self.repo.set_refresh_token_hash(user, None)
            self.repo.commit()
            raise InvalidTokenError()

        token_pair = issue_token_pair(user_id=str(user.id), role=user.role.name)
        self.repo.set_refresh_token_hash(user, token_pair.refresh_token_hash)
        self.repo.commit()

        return token_pair, user

    def logout(self, user: User) -> None:
        self.repo.set_refresh_token_hash(user, None)
        self.repo.commit()

    def change_password(self, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.password_hash):
            raise InvalidCredentialsError()

        self.repo.set_password_hash(user, hash_password(new_password))
        # Force re-login on all devices after a password change.
        self.repo.set_refresh_token_hash(user, None)
        self.repo.commit()

    def create_student(self, full_name: str, email: str, password: str) -> User:
        if self.repo.get_by_email(email) is not None:
            raise EmailAlreadyExistsError()

        student_role = self.repo.get_role_by_name(RoleName.STUDENT.value)
        if student_role is None:
            raise RuntimeError("STUDENT role is not seeded")

        user = self.repo.create_user(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            role_id=student_role.id,
        )
        self.repo.commit()
        self.repo.refresh(user)
        return user


__all__ = [
    "AuthService",
    "InvalidCredentialsError",
    "AccountLockedError",
    "AccountInactiveError",
    "InvalidTokenError",
    "EmailAlreadyExistsError",
    "REFRESH_TOKEN_MAX_AGE_SECONDS",
]
