#!/usr/bin/env python3
"""Validate approved drafts and publish them to HTML posts."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

import markdown
import yaml

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
    "external_sources",
    "internal_links",
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


def validate_frontmatter(data: dict, body: str) -> list[str]:
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing field: {field}")

    if data.get("approved") is not True:
        errors.append("Draft is not approved")

    if data.get("humanization_verified") is not True:
        errors.append("Draft has not passed humanization verification")

    if not isinstance(data.get("external_sources"), list) or len(data.get("external_sources", [])) < 2:
        errors.append("Need at least 2 external sources")

    if not isinstance(data.get("internal_links"), list) or len(data.get("internal_links", [])) < 3:
        errors.append("Need at least 3 internal links")

    word_count = len(re.findall(r"\b\w+\b", body))
    if word_count < 450:
        errors.append("Body too short (minimum 450 words)")

    if len(re.findall(r"^##\s+", body, flags=re.MULTILINE)) < 3:
        errors.append("Need at least 3 H2 sections")

    if len(re.findall(r"^\s*-\s+", body, flags=re.MULTILINE)) < 3:
        errors.append("Need at least 3 bullet points in body")

    primary_keyword = str(data.get("primary_keyword", "")).strip().lower()
    if primary_keyword:
        lower_body = body.lower()
        keyword_count = lower_body.count(primary_keyword)
        if keyword_count > 0 and (keyword_count / max(1, word_count)) > 0.03:
            errors.append("Potential keyword stuffing detected")

    passive_pattern = re.compile(r"\b(?:was|were|is|are|been|be)\s+\w+ed\b", re.IGNORECASE)
    passive_hits = len(passive_pattern.findall(body))
    if passive_hits > 18:
        errors.append("Passive voice usage appears too high")

    clickbait_terms = [
        "you won't believe",
        "shocking",
        "secret trick",
        "guaranteed rank #1",
        "instant results",
    ]
    if any(term in body.lower() for term in clickbait_terms):
        errors.append("Clickbait language detected")

    outdated_years = re.findall(r"\b(2023|2024)\b", body)
    if outdated_years:
        errors.append("Outdated year references detected (2023/2024)")

    jargon_terms = ["lsi", "tf-idf", "pogo-sticking"]
    jargon_hits = sum(body.lower().count(term) for term in jargon_terms)
    if jargon_hits > 2:
        errors.append("Jargon overload detected")

    return errors


def make_links_html(links: list[str], label_prefix: str, external: bool) -> str:
    rows = []
    for idx, url in enumerate(links, start=1):
        target = ' target="_blank" rel="noopener noreferrer"' if external else ""
        rows.append(f'<ul><li><a href="{url}"{target}>{label_prefix} {idx}</a></li></ul>')
    return "\n".join(rows)


def render_html(template: str, data: dict, body_markdown: str) -> str:
    post_html = markdown.markdown(body_markdown, extensions=["tables", "fenced_code"])
    replacements = {
        "{{TITLE}}": str(data["title"]),
        "{{META_DESCRIPTION}}": str(data["meta_description"]),
        "{{CANONICAL_URL}}": str(data["canonical_url"]),
        "{{OG_IMAGE}}": str(data["og_image"]),
        "{{DATE_PUBLISHED}}": str(data["date"]),
        "{{DATE_MODIFIED}}": str(data["date"]),
        "{{PRIMARY_KEYWORD}}": str(data["primary_keyword"]),
        "{{INTRO_HOOK}}": str(data["intro_hook"]),
        "{{FEATURE_IMAGE}}": str(data["feature_image"]),
        "{{FEATURE_IMAGE_ALT}}": str(data["feature_image_alt"]),
        "{{POST_HTML}}": post_html,
        "{{EXTERNAL_SOURCES_HTML}}": make_links_html(data["external_sources"], "External source", True),
        "{{INTERNAL_LINKS_HTML}}": make_links_html(data["internal_links"], "Related resource", False),
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

    errors = validate_frontmatter(data, body)
    if errors:
        return False, f"{draft_path.name}: " + "; ".join(errors)

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
