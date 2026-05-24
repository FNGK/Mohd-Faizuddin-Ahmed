from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import ContentStatus, Page, Post, User, UserRole
from app.schemas import (
    PageCreate,
    PageOut,
    PageUpdate,
    PostCreate,
    PostOut,
    PostUpdate,
    RevisionOut,
)
from app.services.audit import log_action
from app.services.email_notify import notify_content_published, notify_content_review
from app.services.revisions import list_revisions, save_revision, snapshot_page, snapshot_post
from app.services.webhooks import dispatch_event

router = APIRouter(tags=["content"])


def _apply_publish(obj: Page | Post, status_value: ContentStatus | None) -> None:
    if status_value == ContentStatus.published and not obj.published_at:
        obj.published_at = datetime.now(timezone.utc)


def _emit_content_events(
    db: Session,
    *,
    content_type: str,
    row: Page | Post,
    previous_status: ContentStatus,
) -> None:
    if row.status == ContentStatus.published and previous_status != ContentStatus.published:
        payload = {
            "id": row.id,
            "slug": row.slug,
            "title": row.title,
            "locale": getattr(row, "locale", "en"),
            "content_type": content_type,
        }
        dispatch_event(db, "content.published", payload)
        notify_content_published(row.title, content_type, payload["locale"])
    elif row.status == ContentStatus.review and previous_status != ContentStatus.review:
        notify_content_review(row.title, content_type)


@router.get("/pages", response_model=list[PageOut])
def list_pages(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[Page]:
    return list(db.scalars(select(Page).order_by(Page.updated_at.desc())))


@router.post("/pages", response_model=PageOut, status_code=status.HTTP_201_CREATED)
def create_page(
    payload: PageCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.editor)),
) -> Page:
    if db.scalar(
        select(Page).where(Page.slug == payload.slug, Page.locale == payload.locale)
    ):
        raise HTTPException(status_code=400, detail="Slug exists for locale")
    row = Page(**payload.model_dump(), author_id=user.id)
    _apply_publish(row, row.status)
    previous_status = ContentStatus.draft
    db.add(row)
    db.flush()
    save_revision(db, content_type="page", content_id=row.id, snapshot=snapshot_page(row), author_id=user.id)
    _emit_content_events(db, content_type="page", row=row, previous_status=previous_status)
    log_action(db, user=user, action="create", resource_type="page", resource_id=row.id, request=request)
    db.commit()
    db.refresh(row)
    return row


@router.get("/pages/{page_id}", response_model=PageOut)
def get_page(page_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Page:
    row = db.get(Page, page_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return row


@router.patch("/pages/{page_id}", response_model=PageOut)
def update_page(
    page_id: str,
    payload: PageUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.editor)),
) -> Page:
    row = db.get(Page, page_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    previous_status = row.status
    save_revision(db, content_type="page", content_id=row.id, snapshot=snapshot_page(row), author_id=user.id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    _apply_publish(row, row.status)
    _emit_content_events(db, content_type="page", row=row, previous_status=previous_status)
    log_action(db, user=user, action="update", resource_type="page", resource_id=row.id, request=request)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/pages/{page_id}")
def delete_page(
    page_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin)),
) -> dict:
    row = db.get(Page, page_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    log_action(db, user=user, action="delete", resource_type="page", resource_id=page_id, request=request)
    db.commit()
    return {"success": True}


@router.get("/pages/{page_id}/revisions", response_model=list[RevisionOut])
def page_revisions(page_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list_revisions(db, "page", page_id)


@router.get("/posts", response_model=list[PostOut])
def list_posts(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[Post]:
    return list(db.scalars(select(Post).order_by(Post.updated_at.desc())))


@router.post("/posts", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.editor)),
) -> Post:
    if db.scalar(
        select(Post).where(Post.slug == payload.slug, Post.locale == payload.locale)
    ):
        raise HTTPException(status_code=400, detail="Slug exists for locale")
    row = Post(**payload.model_dump(), author_id=user.id)
    _apply_publish(row, row.status)
    db.add(row)
    db.flush()
    save_revision(db, content_type="post", content_id=row.id, snapshot=snapshot_post(row), author_id=user.id)
    _emit_content_events(db, content_type="post", row=row, previous_status=ContentStatus.draft)
    log_action(db, user=user, action="create", resource_type="post", resource_id=row.id, request=request)
    db.commit()
    db.refresh(row)
    return row


@router.get("/posts/{post_id}", response_model=PostOut)
def get_post(post_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Post:
    row = db.get(Post, post_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return row


@router.patch("/posts/{post_id}", response_model=PostOut)
def update_post(
    post_id: str,
    payload: PostUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.editor)),
) -> Post:
    row = db.get(Post, post_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    previous_status = row.status
    save_revision(db, content_type="post", content_id=row.id, snapshot=snapshot_post(row), author_id=user.id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    _apply_publish(row, row.status)
    _emit_content_events(db, content_type="post", row=row, previous_status=previous_status)
    log_action(db, user=user, action="update", resource_type="post", resource_id=row.id, request=request)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin)),
) -> dict:
    row = db.get(Post, post_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    log_action(db, user=user, action="delete", resource_type="post", resource_id=post_id, request=request)
    db.commit()
    return {"success": True}


@router.get("/posts/{post_id}/revisions", response_model=list[RevisionOut])
def post_revisions(post_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list_revisions(db, "post", post_id)
