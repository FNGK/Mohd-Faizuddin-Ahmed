from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import AuditLog, ContactSubmission, ContentStatus, Media, Page, Post, User
from app.schemas import AuditOut, DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> DashboardStats:
    pages_total = db.scalar(select(func.count()).select_from(Page)) or 0
    pages_published = (
        db.scalar(select(func.count()).select_from(Page).where(Page.status == ContentStatus.published)) or 0
    )
    posts_total = db.scalar(select(func.count()).select_from(Post)) or 0
    posts_published = (
        db.scalar(select(func.count()).select_from(Post).where(Post.status == ContentStatus.published)) or 0
    )
    contacts_total = db.scalar(select(func.count()).select_from(ContactSubmission)) or 0
    contacts_new = (
        db.scalar(select(func.count()).select_from(ContactSubmission).where(ContactSubmission.status == "new"))
        or 0
    )
    media_total = db.scalar(select(func.count()).select_from(Media)) or 0
    users_total = db.scalar(select(func.count()).select_from(User)) or 0
    drafts_total = (
        db.scalar(
            select(func.count()).select_from(Page).where(Page.status == ContentStatus.draft)
        )
        or 0
    ) + (
        db.scalar(
            select(func.count()).select_from(Post).where(Post.status == ContentStatus.draft)
        )
        or 0
    )
    return DashboardStats(
        pages_total=pages_total,
        pages_published=pages_published,
        posts_total=posts_total,
        posts_published=posts_published,
        contacts_new=contacts_new,
        contacts_total=contacts_total,
        media_total=media_total,
        users_total=users_total,
        drafts_total=drafts_total,
    )


@router.get("/activity", response_model=list[AuditOut])
def recent_activity(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[AuditOut]:
    rows = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(40))
    out: list[AuditOut] = []
    for row in rows:
        name = row.user.full_name if row.user else None
        out.append(
            AuditOut(
                id=row.id,
                user_id=row.user_id,
                user_name=name,
                action=row.action,
                resource_type=row.resource_type,
                resource_id=row.resource_id,
                ip_address=row.ip_address,
                meta=row.meta,
                created_at=row.created_at,
            )
        )
    return out
