from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.security import decode_access_token


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return ""


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = auth[7:].strip()
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive")
    return user


def require_roles(*roles: UserRole) -> Callable:
    def checker(user: User = Depends(get_current_user)) -> User:
        allowed = {UserRole.superadmin, UserRole.admin, *roles}
        if user.role == UserRole.superadmin:
            return user
        if user.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return checker


RequireAdmin = Depends(require_roles(UserRole.admin))
RequireEditor = Depends(require_roles(UserRole.editor))
