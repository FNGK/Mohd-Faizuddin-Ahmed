import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import User, UserRole, Webhook, WebhookDelivery
from app.schemas import WebhookCreate, WebhookOut, WebhookUpdate
from app.services.audit import log_action
from app.services.permissions import user_has_permission

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def to_out(row: Webhook) -> WebhookOut:
    return WebhookOut(
        id=row.id,
        name=row.name,
        url=row.url,
        secret=row.secret[:8] + "…",
        events=row.events or [],
        is_active=row.is_active,
        created_at=row.created_at,
    )


@router.get("", response_model=list[WebhookOut])
def list_webhooks(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not user_has_permission(db, user, "webhooks.write") and user.role not in (
        UserRole.admin,
        UserRole.superadmin,
    ):
        raise HTTPException(status_code=403, detail="Forbidden")
    return [to_out(w) for w in db.scalars(select(Webhook).order_by(Webhook.created_at.desc()))]


@router.post("", response_model=WebhookOut, status_code=status.HTTP_201_CREATED)
def create_webhook(
    payload: WebhookCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin)),
):
    secret = payload.secret or secrets.token_urlsafe(24)
    row = Webhook(
        name=payload.name,
        url=str(payload.url),
        secret=secret,
        events=payload.events,
        is_active=payload.is_active,
    )
    db.add(row)
    log_action(db, user=user, action="create", resource_type="webhook", resource_id=row.id, request=request)
    db.commit()
    db.refresh(row)
    return to_out(row)


@router.patch("/{webhook_id}", response_model=WebhookOut)
def update_webhook(
    webhook_id: str,
    payload: WebhookUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin)),
):
    row = db.get(Webhook, webhook_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        if key == "url" and value:
            setattr(row, key, str(value))
        else:
            setattr(row, key, value)
    log_action(db, user=user, action="update", resource_type="webhook", resource_id=row.id, request=request)
    db.commit()
    db.refresh(row)
    return to_out(row)


@router.delete("/{webhook_id}")
def delete_webhook(
    webhook_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin)),
):
    row = db.get(Webhook, webhook_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    log_action(db, user=user, action="delete", resource_type="webhook", resource_id=webhook_id, request=request)
    db.commit()
    return {"success": True}


@router.get("/{webhook_id}/deliveries")
def list_deliveries(
    webhook_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin)),
):
    rows = db.scalars(
        select(WebhookDelivery)
        .where(WebhookDelivery.webhook_id == webhook_id)
        .order_by(WebhookDelivery.created_at.desc())
        .limit(50)
    )
    return [
        {
            "id": d.id,
            "event": d.event,
            "success": d.success,
            "status_code": d.status_code,
            "created_at": d.created_at,
        }
        for d in rows
    ]
