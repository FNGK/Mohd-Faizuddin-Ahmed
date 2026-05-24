from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.deps import get_client_ip
from app.models import AuditLog, User


def log_action(
    db: Session,
    *,
    user: User | None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    request: Request | None = None,
    meta: dict[str, Any] | None = None,
) -> AuditLog:
    entry = AuditLog(
        user_id=user.id if user else None,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=get_client_ip(request) if request else None,
        meta=meta,
    )
    db.add(entry)
    db.flush()
    return entry
