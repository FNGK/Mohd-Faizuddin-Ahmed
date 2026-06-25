#!/usr/bin/env python3
"""Validate approved drafts and publish them to HTML posts."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

import markdown
import yaml

from compliance import validate_full_draft

REQUIRED_FIELDS = [
    "title",
    "slug",
    "date",
    "primary_keyword",
    "meta_description",
    "feature_image",
    "feature_image_alt",
    "canonical_url",
    "og_image",
    "intro_hook",
    "approved",
    "editorial_reviewed",
    "external_sources",
    "internal_links",
    "recommended_word_count",
    "serp_intent",
    "funnel_stage",
    "paa_questions",
    "serp_analysis",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and publish approved blog drafts.")
    parser.add_argument("--drafts-dir", default="blog/drafts", help="Draft folder path")
    parser.add_argument("--posts-dir", default="blog/posts", help="Published posts folder path")
    parser.add_argument("--template", default="blog/templates/post-template.html", help="Post template path")
    parser.add_argument("--index-file", default="blog/index.html", help="Blog index file path")
    parser.add_argument("--publish", action="store_true", help="Publish approved drafts")
    return parser.parse_args()


def split_frontmatter(content: str) -> tuple[dict, str]:
    if not content.startswith("---\n"):
        raise ValueError("Draft missing frontmatter header")
    _, rest = content.split("---\n", 1)
    frontmatter_raw, body = rest.split("\n---\n", 1)
    data = yaml.safe_load(frontmatter_raw) or {}
    return data, body.strip()


def validate_frontmatter(data: dict, body: str, *, publishing: bool) -> list[str]:
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in data or data.get(field) in (None, "", []):
            errors.append(f"Missing field: {field}")

    compliance = validate_full_draft(
        data,
        body,
        for_publish=publishing,
        humanization_score=int(data.get("humanization_score") or 0),
        originality_score=int(data.get("originality_score") or 0),
    )
    errors.extend(compliance.errors)
    return errors


# Friendly labels for internal "related" links (path normalized, no ../ prefix).
_INTERNAL_LABELS = {
    "services/index.html": ("Service catalog", "Services"),
    "services/technical-seo.html": ("Technical SEO", "Service"),
    "services/local-seo.html": ("Local SEO", "Service"),
    "services/international-seo.html": ("International SEO", "Service"),
    "services/content-seo.html": ("Content SEO", "Service"),
    "resources/seo-audit-playbook.html": ("SEO audit playbook", "Resource"),
    "case-studies/index.html": ("Case studies", "Proof"),
    "contact/index.html": ("Book a strategy call", "Contact"),
    "free-tools/gsc-error-priority-calculator.html": ("GSC priority calculator", "Free tool"),
}


def _internal_key(url: str) -> str:
    return re.sub(r"^(\.\./)+", "", url).lstrip("./")


def _external_label(url: str) -> str:
    try:
        parsed = urlparse(url)
        host = parsed.netloc.replace("www.", "")
        segs = [s for s in parsed.path.split("/") if s and not s.endswith((".html", ".php"))]
        if segs:
            title = segs[-1].replace("-", " ").replace("_", " ").strip().title()
            return f"{host} — {title}"
        return host
    except Exception:
        return url


def build_reference_items(urls: list[str]) -> str:
    rows = []
    for url in urls:
        rows.append(
            f'    <li><a href="{url}" target="_blank" rel="noopener noreferrer">{_external_label(url)}</a></li>'
        )
    return "\n".join(rows)


def build_related_cards(links: list[str]) -> str:
    cards = []
    for url in links:
        key = _internal_key(url)
        if key in _INTERNAL_LABELS:
            title, eyebrow = _INTERNAL_LABELS[key]
        else:
            title = key.rsplit("/", 1)[-1].replace(".html", "").replace("-", " ").title()
            eyebrow = "Resource"
        cards.append(
            f'    <a class="related-post" href="{url}">\n'
            f'      <span class="related-post__eyebrow">{eyebrow}</span>\n'
            f'      <h3>{title}</h3>\n'
            f'      <span class="go">Read &rarr;</span>\n'
            f"    </a>"
        )
    return "\n".join(cards)


def get_faqs(data: dict) -> list[tuple[str, str]]:
    """FAQs come from an explicit frontmatter `faqs` list of {question, answer}.

    This is intentional: deriving FAQs from every `###` heading (the old
    behavior) mislabeled normal subheadings as Q&A and duplicated them on the
    page. Explicit faqs give clean, valid FAQPage schema and a real accordion.
    """
    out = []
    for item in data.get("faqs") or []:
        q = str(item.get("question", "")).strip()
        a = str(item.get("answer", "")).strip()
        if q and a:
            out.append((q, a))
    return out


def build_faq_schema(faqs: list[tuple[str, str]]) -> str:
    if not faqs:
        return ""
    payload = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a[:600]}}
            for q, a in faqs[:8]
        ],
    }
    return json.dumps(payload, ensure_ascii=True)


def build_faq_visible(faqs: list[tuple[str, str]]) -> str:
    if not faqs:
        return ""
    items = "\n".join(
        f"    <details><summary>{q}</summary><p>{a}</p></details>" for q, a in faqs[:8]
    )
    return (
        '<h2>Frequently asked questions</h2>\n'
        '          <div class="post-faq">\n'
        f"{items}\n"
        "          </div>"
    )


def build_key_takeaways(data: dict) -> str:
    items = data.get("key_takeaways") or []
    if not items:
        return ""
    lis = "\n".join(f"      <li>{x}</li>" for x in items)
    return (
        '<aside class="key-takeaways" aria-label="Key takeaways">\n'
        '            <p class="key-takeaways__title">Key takeaways</p>\n'
        f"            <ul>\n{lis}\n            </ul>\n"
        "          </aside>"
    )


def build_breadcrumb_schema(data: dict) -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://seowithfaiz.com/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://seowithfaiz.com/blog/"},
            {"@type": "ListItem", "position": 3, "name": str(data["title"]), "item": str(data["canonical_url"])},
        ],
    }
    return (
        '<script type="application/ld+json">\n  '
        + json.dumps(payload, ensure_ascii=True)
        + "\n  </script>"
    )


def _word_count(body_markdown: str) -> int:
    text = re.sub(r"[#*`>\[\]()_-]", " ", body_markdown)
    return len(re.findall(r"\b\w+\b", text))


def _date_display(date_str: str) -> str:
    try:
        d = _dt.datetime.strptime(str(date_str), "%Y-%m-%d")
        return f"{d.strftime('%B')} {d.day}, {d.year}"
    except Exception:
        return str(date_str)


def render_html(template: str, data: dict, body_markdown: str) -> str:
    post_html = markdown.markdown(body_markdown, extensions=["tables", "fenced_code"])
    faqs = get_faqs(data)
    faq_schema = build_faq_schema(faqs)
    article_schema_extra = f',\n    "subjectOf": {faq_schema}' if faq_schema else ""
    words = _word_count(body_markdown)
    read_time = max(1, round(words / 220))
    replacements = {
        "{{TITLE}}": str(data["title"]),
        "{{META_DESCRIPTION}}": str(data["meta_description"]),
        "{{CANONICAL_URL}}": str(data["canonical_url"]),
        "{{OG_IMAGE}}": str(data["og_image"]),
        "{{DATE_PUBLISHED}}": str(data["date"]),
        "{{DATE_MODIFIED}}": str(data.get("date_modified") or data["date"]),
        "{{DATE_DISPLAY}}": _date_display(data["date"]),
        "{{READ_TIME}}": str(read_time),
        "{{WORD_COUNT}}": str(words),
        "{{PRIMARY_KEYWORD}}": str(data["primary_keyword"]),
        "{{INTRO_HOOK}}": str(data["intro_hook"]),
        "{{FEATURE_IMAGE}}": str(data["feature_image"]),
        "{{FEATURE_IMAGE_ALT}}": str(data["feature_image_alt"]),
        "{{KEY_TAKEAWAYS_HTML}}": build_key_takeaways(data),
        "{{POST_HTML}}": post_html,
        "{{FAQ_HTML}}": build_faq_visible(faqs),
        "{{EXTERNAL_SOURCES_HTML}}": build_reference_items(data["external_sources"]),
        "{{INTERNAL_LINKS_HTML}}": build_related_cards(data["internal_links"]),
        "{{FAQ_SCHEMA_EXTRA}}": article_schema_extra,
        "{{BREADCRUMB_SCHEMA}}": build_breadcrumb_schema(data),
    }
    html = template
    for key, value in replacements.items():
        html = html.replace(key, value)
    return html


def update_blog_index(index_path: Path, data: dict) -> None:
    content = index_path.read_text(encoding="utf-8")
    slug = data["slug"]
    href = f"./posts/{slug}.html"
    if href in content:
        return

    start_marker = "<!-- AUTO_BLOG_CARDS_START -->"
    end_marker = "<!-- AUTO_BLOG_CARDS_END -->"
    if start_marker not in content or end_marker not in content:
        return

    card = (
        f'\n        <article class="blog-card">\n'
        f'          <span class="meta">Published · {data["date"]} · 8 min read</span>\n'
        f'          <h2 style="font-size:1.4rem;">{data["title"]}</h2>\n'
        f'          <p>{data["meta_description"]}</p>\n'
        f'          <a class="btn btn-secondary" href="{href}">Read article</a>\n'
        f"        </article>\n"
    )

    start_idx = content.index(start_marker) + len(start_marker)
    content = content[:start_idx] + card + content[start_idx:]
    index_path.write_text(content, encoding="utf-8")


def process_draft(
    draft_path: Path,
    template_text: str,
    posts_dir: Path,
    index_path: Path,
    publish: bool,
) -> tuple[bool, str]:
    try:
        data, body = split_frontmatter(draft_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"{draft_path.name}: parse error ({exc})"

    errors = validate_frontmatter(data, body, publishing=publish)
    if errors:
        return False, f"{draft_path.name}: " + "; ".join(errors[:8]) + (
            f" (+{len(errors) - 8} more)" if len(errors) > 8 else ""
        )

    if publish:
        post_path = posts_dir / f"{data['slug']}.html"
        html = render_html(template_text, data, body)
        post_path.write_text(html, encoding="utf-8")
        update_blog_index(index_path, data)

        archive_dir = draft_path.parent / "published"
        archive_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(draft_path), str(archive_dir / draft_path.name))
        return True, f"{draft_path.name}: published -> {post_path.name}"

    return True, f"{draft_path.name}: valid"


def main() -> None:
    args = parse_args()
    drafts_dir = Path(args.drafts_dir)
    posts_dir = Path(args.posts_dir)
    template_path = Path(args.template)
    index_path = Path(args.index_file)

    posts_dir.mkdir(parents=True, exist_ok=True)

    if not drafts_dir.exists():
        raise FileNotFoundError(f"Drafts directory not found: {drafts_dir}")
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    if not index_path.exists():
        raise FileNotFoundError(f"Index file not found: {index_path}")

    template_text = template_path.read_text(encoding="utf-8")
    if "{{FAQ_SCHEMA_EXTRA}}" not in template_text:
        template_text = template_text.replace(
            '"mainEntityOfPage": "{{CANONICAL_URL}}"',
            '"mainEntityOfPage": "{{CANONICAL_URL}}"{{FAQ_SCHEMA_EXTRA}}',
        )

    draft_files = sorted(p for p in drafts_dir.glob("*.md") if p.name.lower() != "readme.md")
    if not draft_files:
        print("No draft files to process.")
        return

    success_count = 0
    for draft_file in draft_files:
        ok, message = process_draft(draft_file, template_text, posts_dir, index_path, args.publish)
        print(message)
        if ok:
            success_count += 1

    print(f"Processed drafts: {len(draft_files)} | Passed: {success_count} | Publish mode: {args.publish}")


if __name__ == "__main__":
    main()
