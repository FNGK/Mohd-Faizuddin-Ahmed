from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from app.models import ContentStatus, UserRole


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=120)
    role: UserRole = UserRole.editor
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=10, max_length=128)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=10, max_length=128)


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    avatar_url: str | None
    last_login_at: datetime | None
    totp_enabled: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class PageBase(BaseModel):
    slug: str = Field(min_length=1, max_length=200)
    locale: str = Field(default="en", max_length=10)
    title: str = Field(min_length=1, max_length=300)
    excerpt: str | None = None
    body_html: str = ""
    status: ContentStatus = ContentStatus.draft
    template: str = "default"
    seo_title: str | None = None
    seo_description: str | None = None
    canonical_url: str | None = None
    og_image_id: str | None = None
    publish_path: str | None = None
    scheduled_at: datetime | None = None


class PageCreate(PageBase):
    pass


class PageUpdate(BaseModel):
    slug: str | None = None
    locale: str | None = None
    title: str | None = None
    excerpt: str | None = None
    body_html: str | None = None
    status: ContentStatus | None = None
    template: str | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    canonical_url: str | None = None
    og_image_id: str | None = None
    publish_path: str | None = None
    scheduled_at: datetime | None = None


class PageOut(PageBase):
    id: str
    author_id: str | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PostBase(BaseModel):
    slug: str = Field(min_length=1, max_length=200)
    locale: str = Field(default="en", max_length=10)
    title: str = Field(min_length=1, max_length=300)
    excerpt: str | None = None
    body_html: str = ""
    status: ContentStatus = ContentStatus.draft
    primary_keyword: str | None = None
    intro_hook: str | None = None
    tags: list[str] = Field(default_factory=list)
    seo_title: str | None = None
    seo_description: str | None = None
    featured_image_id: str | None = None


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    slug: str | None = None
    locale: str | None = None
    title: str | None = None
    excerpt: str | None = None
    body_html: str | None = None
    status: ContentStatus | None = None
    primary_keyword: str | None = None
    intro_hook: str | None = None
    tags: list[str] | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    featured_image_id: str | None = None


class PostOut(PostBase):
    id: str
    author_id: str | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MediaOut(BaseModel):
    id: str
    filename: str
    stored_path: str
    mime_type: str
    size_bytes: int
    width: int | None
    height: int | None
    alt_text: str | None
    folder: str
    url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ContactIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    website: str = Field(min_length=4, max_length=500)
    region: str = Field(min_length=1, max_length=40)
    goal: str = Field(min_length=12, max_length=4000)
    honeypot: str = ""


class ContactOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    website: str
    region: str
    goal: str
    status: str
    notes: str | None
    email_delivered: bool
    created_at: datetime
    read_at: datetime | None

    model_config = {"from_attributes": True}


class ContactStatusUpdate(BaseModel):
    status: str = Field(pattern="^(new|read|replied|archived)$")
    notes: str | None = None


class AuditOut(BaseModel):
    id: str
    user_id: str | None
    user_name: str | None = None
    action: str
    resource_type: str
    resource_id: str | None
    ip_address: str | None
    meta: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    pages_total: int
    pages_published: int
    posts_total: int
    posts_published: int
    contacts_new: int
    contacts_total: int
    media_total: int
    users_total: int
    drafts_total: int


class SettingOut(BaseModel):
    key: str
    value: Any
    updated_at: datetime

    model_config = {"from_attributes": True}


class SettingUpdate(BaseModel):
    value: Any


class MenuItemOut(BaseModel):
    id: str
    location: str
    label: str
    url: str
    sort_order: int
    parent_id: str | None
    is_visible: bool

    model_config = {"from_attributes": True}


class MenuItemCreate(BaseModel):
    location: str
    label: str
    url: str
    sort_order: int = 0
    parent_id: str | None = None
    is_visible: bool = True


class RevisionOut(BaseModel):
    id: str
    content_type: str
    content_id: str
    snapshot: dict[str, Any]
    author_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class WebhookCreate(BaseModel):
    name: str
    url: str
    events: list[str] = Field(default_factory=list)
    secret: str | None = None
    is_active: bool = True


class WebhookUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    events: list[str] | None = None
    is_active: bool | None = None


class WebhookOut(BaseModel):
    id: str
    name: str
    url: str
    secret: str
    events: list[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TranslationCreate(BaseModel):
    content_type: str
    parent_id: str
    locale: str
    slug: str | None = None
    title: str
    excerpt: str | None = None
    body_html: str = ""
    seo_title: str | None = None
    seo_description: str | None = None
    status: ContentStatus = ContentStatus.draft


class TranslationUpdate(BaseModel):
    slug: str | None = None
    title: str | None = None
    excerpt: str | None = None
    body_html: str | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    status: ContentStatus | None = None


class TranslationOut(BaseModel):
    id: str
    content_type: str
    parent_id: str
    locale: str
    slug: str | None
    title: str
    excerpt: str | None
    body_html: str
    seo_title: str | None
    seo_description: str | None
    status: ContentStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RolePermissionOut(BaseModel):
    id: str
    role: UserRole
    permission: str
    allowed: bool

    model_config = {"from_attributes": True}


class RolePermissionUpdate(BaseModel):
    role: UserRole
    permission: str
    allowed: bool
