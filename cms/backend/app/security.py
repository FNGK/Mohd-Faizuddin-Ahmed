import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.config import get_settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    payload = {"sub": subject, "exp": expire, "type": "access"}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token_value() -> str:
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    if payload.get("type") != "access":
        raise JWTError("Invalid token type")
    return payload


def refresh_expiry() -> datetime:
    settings = get_settings()
    return datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_days)


def create_totp_pending_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    payload = {"sub": user_id, "exp": expire, "type": "totp_pending"}
    return jwt.encode(payload, get_settings().secret_key, algorithm=ALGORITHM)


def decode_totp_pending_token(token: str) -> str:
    try:
        payload = jwt.decode(token, get_settings().secret_key, algorithms=[ALGORITHM])
    except JWTError:
        raise
    if payload.get("type") != "totp_pending":
        raise JWTError("Invalid pending token")
    return str(payload["sub"])
