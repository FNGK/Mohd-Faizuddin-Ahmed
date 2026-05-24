import html
import re
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import REPO_ROOT
from app.models import ContentStatus, Page, Post

BLOG_INDEX = REPO_ROOT / "blog" / "index.html"
POST_TEMPLATE = REPO_ROOT / "blog" / "templates" / "post-template.html"
POSTS_DIR = REPO_ROOT / "blog" / "posts"
CARDS_START = "<!-- AUTO_BLOG_CARDS_START -->"
CARDS_END = "<!-- AUTO_BLOG_CARDS_END -->"
DEFAULT_OG = "https://seowithfaiz.com/assets/og/og-default.png"
SITE_URL = "https://seowithfaiz.com"


def _site_url() -> str:
    return SITE_URL.rstrip("/")


def _read_template() -> str:
    return POST_TEMPLATE.read_text(encoding="utf-8")


def _format_date(dt: datetime | None) -> str:
    if not dt:
        dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%d")


def _format_meta_date(dt: datetime | None) -> str:
    if not dt:
        dt = datetime.now(timezone.utc)
    return dt.strftime("%B %Y")


def _estimate_read_minutes(html_body: str) -> int:
    text = re.sub(r"<[^>]+>", " ", html_body or "")
    words = len(text.split())
    return max(3, round(words / 220))


def render_post_html(post: Post) -> str:
    tpl = _read_template()
    canonical = f"{_site_url()}/blog/posts/{post.slug}.html"
    title = post.seo_title or post.title
    description = post.seo_description or post.excerpt or post.title
    keyword = post.primary_keyword or (post.tags[0] if post.tags else "SEO strategy")
    intro = post.intro_hook or post.excerpt or description
    replacements = {
        "{{TITLE}}": html.escape(title),
        "{{META_DESCRIPTION}}": html.escape(description),
        "{{CANONICAL_URL}}": canonical,
        "{{OG_IMAGE}}": DEFAULT_OG,
        "{{DATE_PUBLISHED}}": _format_date(post.published_at),
        "{{DATE_MODIFIED}}": _format_date(post.updated_at),
        "{{PRIMARY_KEYWORD}}": html.escape(keyword),
        "{{INTRO_HOOK}}": html.escape(intro),
        "{{FEATURE_IMAGE}}": "../../assets/og/og-default.png",
        "{{FEATURE_IMAGE_ALT}}": html.escape(title),
        "{{POST_HTML}}": post.body_html or "",
        "{{EXTERNAL_SOURCES_HTML}}": "<p><em>Add references in the CMS body or extend publish metadata.</em></p>",
        "{{INTERNAL_LINKS_HTML}}": "<ul><li><a href=\"../../services/index.html\">Services</a></li><li><a href=\"../../contact/index.html\">Contact</a></li></ul>",
    }
    out = tpl
    for key, value in replacements.items():
        out = out.replace(key, value)
    return out


def _blog_card(post: Post) -> str:
    mins = _estimate_read_minutes(post.body_html)
    meta = f"Published · {_format_meta_date(post.published_at)} · {mins} min read"
    excerpt = html.escape(post.excerpt or post.seo_description or "")
    return f"""
        <article class="blog-card">
          <span class="meta">{meta}</span>
          <h2 style="font-size:1.4rem;">{html.escape(post.title)}</h2>
          <p>{excerpt}</p>
          <a class="btn btn-secondary" href="./posts/{html.escape(post.slug)}.html">Read article</a>
        </article>"""


def rebuild_blog_index(posts: list[Post]) -> Path:
    content = BLOG_INDEX.read_text(encoding="utf-8")
    cards = "\n".join(_blog_card(p) for p in posts)
    if CARDS_START not in content or CARDS_END not in content:
        raise ValueError("blog/index.html missing AUTO_BLOG_CARDS markers")
    pattern = re.compile(
        re.escape(CARDS_START) + r"[\s\S]*?" + re.escape(CARDS_END),
        re.MULTILINE,
    )
    replacement = f"{CARDS_START}\n{cards}\n        {CARDS_END}"
    updated = pattern.sub(replacement, content, count=1)
    BLOG_INDEX.write_text(updated, encoding="utf-8")
    return BLOG_INDEX


def publish_page_html(page: Page) -> Path:
    if page.publish_path:
        dest = REPO_ROOT / page.publish_path.replace("\\", "/").lstrip("/")
    else:
        dest = REPO_ROOT / "pages" / "cms" / f"{page.slug}.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    doc = f"""<!DOCTYPE html>
<html lang="{html.escape(page.locale)}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(page.seo_title or page.title)} | SEO With Faiz</title>
  <meta name="description" content="{html.escape(page.seo_description or page.excerpt or '')}">
  <link rel="canonical" href="{html.escape(page.canonical_url or _site_url() + '/' + page.slug)}">
  <link rel="stylesheet" href="../assets/css/site.css">
  <link rel="stylesheet" href="../assets/css/components.css">
</head>
<body class="page-inner">
<main id="main" class="section"><div class="container post-body">
<h1>{html.escape(page.title)}</h1>
{page.body_html}
</div></main>
<script src="../assets/js/site.js" defer></script>
</body>
</html>"""
    dest.write_text(doc, encoding="utf-8")
    return dest


def publish_all(db: Session, locale: str = "en") -> dict:
    posts = list(
        db.scalars(
            select(Post)
            .where(Post.status == ContentStatus.published, Post.locale == locale)
            .order_by(Post.published_at.desc())
        )
    )
    pages = list(
        db.scalars(
            select(Page)
            .where(Page.status == ContentStatus.published, Page.locale == locale)
            .order_by(Page.updated_at.desc())
        )
    )
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    written_posts: list[str] = []
    for post in posts:
        path = POSTS_DIR / f"{post.slug}.html"
        path.write_text(render_post_html(post), encoding="utf-8")
        written_posts.append(str(path.relative_to(REPO_ROOT)).replace("\\", "/"))

    index_path = rebuild_blog_index(posts) if posts else None
    written_pages: list[str] = []
    for page in pages:
        path = publish_page_html(page)
        written_pages.append(str(path.relative_to(REPO_ROOT)).replace("\\", "/"))

    return {
        "posts_published": len(written_posts),
        "pages_published": len(written_pages),
        "blog_index": str(index_path.relative_to(REPO_ROOT)).replace("\\", "/") if index_path else None,
        "files": written_posts + written_pages,
    }
