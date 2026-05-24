from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models import ContentRevision, Page, Post


def snapshot_page(page: Page) -> dict[str, Any]:
    return {
        "slug": page.slug,
        "title": page.title,
        "excerpt": page.excerpt,
        "body_html": page.body_html,
        "status": page.status.value if page.status else None,
        "template": page.template,
        "seo_title": page.seo_title,
        "seo_description": page.seo_description,
    }


def snapshot_post(post: Post) -> dict[str, Any]:
    return {
        "slug": post.slug,
        "title": post.title,
        "excerpt": post.excerpt,
        "body_html": post.body_html,
        "status": post.status.value if post.status else None,
        "tags": post.tags,
        "seo_title": post.seo_title,
        "seo_description": post.seo_description,
    }


def save_revision(
    db: Session,
    *,
    content_type: str,
    content_id: str,
    snapshot: dict[str, Any],
    author_id: str | None,
) -> ContentRevision:
    rev = ContentRevision(
        content_type=content_type,
        content_id=content_id,
        snapshot=snapshot,
        author_id=author_id,
    )
    db.add(rev)
    db.flush()
    return rev


def list_revisions(db: Session, content_type: str, content_id: str, limit: int = 25) -> list[ContentRevision]:
    return list(
        db.scalars(
            select(ContentRevision)
            .where(
                ContentRevision.content_type == content_type,
                ContentRevision.content_id == content_id,
            )
            .order_by(desc(ContentRevision.created_at))
            .limit(limit)
        )
    )
