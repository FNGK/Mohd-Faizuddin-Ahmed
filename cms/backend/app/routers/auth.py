from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import get_client_ip, get_current_user
from app.models import RefreshToken, User
from app.schemas import LoginRequest, RefreshRequest, TokenResponse, UserOut
from app.security import (
    create_access_token,
    create_refresh_token_value,
    create_totp_pending_token,
    decode_totp_pending_token,
    hash_password,
    hash_token,
    refresh_expiry,
    verify_password,
)
from app.services.audit import log_action
from app.services.totp import generate_secret, provisioning_uri, verify_code
from app.services.webhooks import dispatch_event

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginResponse(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int | None = None
    requires_totp: bool = False
    totp_token: str | None = None


class TotpLoginRequest(BaseModel):
    totp_token: str
    code: str = Field(min_length=6, max_length=8)


class TotpSetupResponse(BaseModel):
    secret: str
    provisioning_uri: str
    enabled: bool


class TotpEnableRequest(BaseModel):
    code: str


def _issue_tokens(user: User, request: Request, db: Session) -> TokenResponse:
    user.last_login_at = datetime.now(timezone.utc)
    access = create_access_token(user.id, {"role": user.role.value})
    refresh_value = create_refresh_token_value()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_value),
            expires_at=refresh_expiry(),
            user_agent=request.headers.get("User-Agent", "")[:500],
            ip_address=get_client_ip(request),
        )
    )
    settings = get_settings()
    return TokenResponse(
        access_token=access,
        refresh_token=refresh_value,
        expires_in=settings.access_token_minutes * 60,
    )


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if user.totp_enabled and user.totp_secret:
        pending = create_totp_pending_token(user.id)
        return LoginResponse(requires_totp=True, totp_token=pending)

    tokens = _issue_tokens(user, request, db)
    log_action(db, user=user, action="login", resource_type="user", resource_id=user.id, request=request)
    dispatch_event(db, "user.login", {"user_id": user.id, "email": user.email})
    db.commit()
    return LoginResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_in=tokens.expires_in,
    )


@router.post("/login/totp", response_model=TokenResponse)
def login_totp(payload: TotpLoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        user_id = decode_totp_pending_token(payload.totp_token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired TOTP session") from exc
    user = db.get(User, user_id)
    if not user or not user.is_active or not user.totp_secret:
        raise HTTPException(status_code=401, detail="Invalid user")
    if not verify_code(user.totp_secret, payload.code):
        raise HTTPException(status_code=401, detail="Invalid authenticator code")
    tokens = _issue_tokens(user, request, db)
    log_action(db, user=user, action="login_totp", resource_type="user", resource_id=user.id, request=request)
    db.commit()
    return tokens


@router.post("/totp/setup", response_model=TotpSetupResponse)
def totp_setup(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> TotpSetupResponse:
    if not user.totp_secret:
        user.totp_secret = generate_secret()
        db.commit()
    return TotpSetupResponse(
        secret=user.totp_secret,
        provisioning_uri=provisioning_uri(user.totp_secret, user.email),
        enabled=user.totp_enabled,
    )


@router.post("/totp/enable")
def totp_enable(
    payload: TotpEnableRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if not user.totp_secret or not verify_code(user.totp_secret, payload.code):
        raise HTTPException(status_code=400, detail="Invalid code")
    user.totp_enabled = True
    db.commit()
    return {"success": True, "totp_enabled": True}


@router.post("/totp/disable")
def totp_disable(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    user.totp_enabled = False
    user.totp_secret = None
    db.commit()
    return {"success": True}


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    token_hash = hash_token(payload.refresh_token)
    row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    if not row or row.revoked or row.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = db.get(User, row.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive")

    row.revoked = True
    new_refresh = create_refresh_token_value()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_token(new_refresh),
            expires_at=refresh_expiry(),
            user_agent=request.headers.get("User-Agent", "")[:500],
            ip_address=get_client_ip(request),
        )
    )
    access = create_access_token(user.id, {"role": user.role.value})
    db.commit()
    settings = get_settings()
    return TokenResponse(
        access_token=access,
        refresh_token=new_refresh,
        expires_in=settings.access_token_minutes * 60,
    )


@router.post("/logout")
def logout(payload: RefreshRequest, db: Session = Depends(get_db)) -> dict:
    token_hash = hash_token(payload.refresh_token)
    row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    if row:
        row.revoked = True
        db.commit()
    return {"success": True}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        avatar_url=user.avatar_url,
        last_login_at=user.last_login_at,
        totp_enabled=user.totp_enabled,
        created_at=user.created_at,
    )
