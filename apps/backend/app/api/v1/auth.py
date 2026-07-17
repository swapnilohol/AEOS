from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models import RoleName, User
from app.schemas.auth import (
    AccessTokenData,
    ChangePasswordRequest,
    CreateStudentRequest,
    LoginRequest,
    UserPublic,
)
from app.schemas.response import ApiResponse
from app.services.auth_service import (
    AccountInactiveError,
    AccountLockedError,
    AuthService,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.services.token_service import ACCESS_TOKEN_MAX_AGE_SECONDS, REFRESH_TOKEN_MAX_AGE_SECONDS, TokenPair

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookies(response: Response, tokens: TokenPair) -> None:
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        max_age=ACCESS_TOKEN_MAX_AGE_SECONDS,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        max_age=REFRESH_TOKEN_MAX_AGE_SECONDS,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")


def _to_public(user: User) -> UserPublic:
    return UserPublic(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=user.role.name,
        is_active=user.is_active,
        last_login_at=user.last_login_at,
    )


@router.post("/login", response_model=ApiResponse[AccessTokenData])
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        tokens, user = service.login(payload.email, payload.password)
    except AccountLockedError:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account temporarily locked due to multiple failed login attempts",
        )
    except AccountInactiveError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    _set_auth_cookies(response, tokens)
    data = AccessTokenData(
        access_token=tokens.access_token,
        expires_in=ACCESS_TOKEN_MAX_AGE_SECONDS,
        user=_to_public(user),
    )
    return ApiResponse(success=True, message="Login successful", data=data)


@router.post("/refresh", response_model=ApiResponse[AccessTokenData])
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    service = AuthService(db)
    try:
        tokens, user = service.refresh(refresh_token)
    except InvalidTokenError:
        _clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token"
        )

    _set_auth_cookies(response, tokens)
    data = AccessTokenData(
        access_token=tokens.access_token,
        expires_in=ACCESS_TOKEN_MAX_AGE_SECONDS,
        user=_to_public(user),
    )
    return ApiResponse(success=True, message="Token refreshed", data=data)


@router.post("/logout", response_model=ApiResponse[None])
def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    AuthService(db).logout(current_user)
    _clear_auth_cookies(response)
    return ApiResponse(success=True, message="Logged out successfully", data=None)


@router.get("/me", response_model=ApiResponse[UserPublic])
def me(current_user: User = Depends(get_current_user)):
    return ApiResponse(success=True, message="ok", data=_to_public(current_user))


@router.post("/change-password", response_model=ApiResponse[None])
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    try:
        service.change_password(current_user, payload.current_password, payload.new_password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect"
        )
    return ApiResponse(success=True, message="Password updated successfully", data=None)


@router.post("/admin/create-student", response_model=ApiResponse[UserPublic])
def create_student(
    payload: CreateStudentRequest,
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    try:
        student = service.create_student(payload.full_name, payload.email, payload.password)
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    return ApiResponse(success=True, message="Student account created", data=_to_public(student))
