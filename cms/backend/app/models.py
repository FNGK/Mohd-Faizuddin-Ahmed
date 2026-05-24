import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    superadmin = "superadmin"
    admin = "admin"
    editor = "editor"
    viewer = "viewer"


class ContentStatus(str, enum.Enum):
    draft = "draft"
    review = "review"
    scheduled = "scheduled"
    published = "published"
    archived = "archived"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.editor)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    totp_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)
    totp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)

    user: Mapped[User] = relationship(back_populates="refresh_tokens")


class Page(Base):
    __tablename__ = "pages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    slug: Mapped[str] = mapped_column(String(200), index=True)
    locale: Mapped[str] = mapped_column(String(10), default="en", index=True)
    title: Mapped[str] = mapped_column(String(300))
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_html: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[ContentStatus] = mapped_column(Enum(ContentStatus), default=ContentStatus.draft)
    template: Mapped[str] = mapped_column(String(80), default="default")
    publish_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    seo_title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    seo_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    canonical_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    og_image_id: Mapped[str | None] = mapped_column(ForeignKey("media.id"), nullable=True)
    author_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    __table_args__ = (UniqueConstraint("slug", "locale", name="uq_page_slug_locale"),)


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    slug: Mapped[str] = mapped_column(String(200), index=True)
    locale: Mapped[str] = mapped_column(String(10), default="en", index=True)
    title: Mapped[str] = mapped_column(String(300))
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_html: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[ContentStatus] = mapped_column(Enum(ContentStatus), default=ContentStatus.draft)
    primary_keyword: Mapped[str | None] = mapped_column(String(200), nullable=True)
    intro_hook: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list | None] = mapped_column(JSON, default=list)
    seo_title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    seo_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    featured_image_id: Mapped[str | None] = mapped_column(ForeignKey("media.id"), nullable=True)
    author_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    __table_args__ = (UniqueConstraint("slug", "locale", name="uq_post_slug_locale"),)


class Media(Base):
    __tablename__ = "media"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    filename: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(500))
    mime_type: Mapped[str] = mapped_column(String(120))
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    alt_text: Mapped[str | None] = mapped_column(String(300), nullable=True)
    folder: Mapped[str] = mapped_column(String(80), default="general")
    uploaded_by_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class MenuItem(Base):
    __tablename__ = "menu_items"
    __table_args__ = (UniqueConstraint("location", "sort_order", name="uq_menu_location_order"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    location: Mapped[str] = mapped_column(String(40), index=True)
    label: Mapped[str] = mapped_column(String(120))
    url: Mapped[str] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("menu_items.id"), nullable=True)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)


class SiteSetting(Base):
    __tablename__ = "site_settings"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    value: Mapped[dict | list | str | int | float | bool | None] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )
    updated_by_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)


class ContactSubmission(Base):
    __tablename__ = "contact_submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254))
    website: Mapped[str] = mapped_column(String(500))
    region: Mapped[str] = mapped_column(String(40))
    goal: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="new")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    email_delivered: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(80), index=True)
    resource_type: Mapped[str] = mapped_column(String(80), index=True)
    resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    user: Mapped[User | None] = relationship(back_populates="audit_logs")


class ContentRevision(Base):
    __tablename__ = "content_revisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    content_type: Mapped[str] = mapped_column(String(20), index=True)
    content_id: Mapped[str] = mapped_column(String(36), index=True)
    snapshot: Mapped[dict] = mapped_column(JSON)
    author_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ContentTranslation(Base):
    __tablename__ = "content_translations"
    __table_args__ = (
        UniqueConstraint("content_type", "parent_id", "locale", name="uq_translation_locale"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    content_type: Mapped[str] = mapped_column(String(20), index=True)
    parent_id: Mapped[str] = mapped_column(String(36), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    slug: Mapped[str | None] = mapped_column(String(200), nullable=True)
    title: Mapped[str] = mapped_column(String(300))
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_html: Mapped[str] = mapped_column(Text, default="")
    seo_title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    seo_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ContentStatus] = mapped_column(Enum(ContentStatus), default=ContentStatus.draft)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (UniqueConstraint("role", "permission", name="uq_role_permission"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole))
    permission: Mapped[str] = mapped_column(String(80))
    allowed: Mapped[bool] = mapped_column(Boolean, default=True)


class Webhook(Base):
    __tablename__ = "webhooks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(120))
    url: Mapped[str] = mapped_column(String(500))
    secret: Mapped[str] = mapped_column(String(128))
    events: Mapped[list] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    webhook_id: Mapped[str] = mapped_column(ForeignKey("webhooks.id", ondelete="CASCADE"))
    event: Mapped[str] = mapped_column(String(80))
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
