#!/usr/bin/env python3
"""Generate review-only blog drafts from keyword plan."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from draft_io import dump_frontmatter
from intent_content import build_body, human_title


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate markdown blog drafts.")
    parser.add_argument(
        "--input",
        default="automation/blog/data/keyword_plan.json",
        help="Keyword plan JSON path",
    )
    parser.add_argument(
        "--output-dir",
        default="blog/drafts",
        help="Draft output directory",
    )
    parser.add_argument(
        "--max-drafts",
        type=int,
        default=2,
        help="Maximum drafts to generate per run",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def draft_exists(slug: str, drafts_dir: Path) -> bool:
    return (drafts_dir / f"{slug}.md").exists() or (Path("blog/posts") / f"{slug}.html").exists()


def first_sentence(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        return stripped
    return "Practical guidance for teams that need search visibility tied to pipeline outcomes."


def build_markdown(idea: dict) -> str:
    now = datetime.now(timezone.utc).date().isoformat()
    intent_cluster = idea.get("intent_cluster", "commercial seo")
    term = str(idea.get("primary_keyword", "")).replace(" seo strategy", "").strip() or idea.get("slug", "seo")
    title = idea.get("title") or human_title(term, intent_cluster)
    slug = idea["slug"]
    primary_keyword = idea["primary_keyword"]
    body = build_body(idea)
    intro_hook = first_sentence(body)
    meta_description = (
        f"{intro_hook[:150].rstrip('.')} "
        "Actionable steps for technical SEO, local growth, and AI-era visibility."
    ).strip()
    feature_image = "../../assets/projects/unstop-seo-audit.png"
    feature_image_alt = "SEO strategy implementation visual"
    canonical_url = f"https://fngk.github.io/Mohd-Faizuddin-Ahmed/blog/posts/{slug}.html"
    og_image = "https://fngk.github.io/Mohd-Faizuddin-Ahmed/assets/og/og-default.png"
    external_sources = idea["external_sources"]
    internal_links = idea["internal_links"]

    frontmatter = {
        "title": title,
        "slug": slug,
        "date": now,
        "primary_keyword": primary_keyword,
        "meta_description": meta_description,
        "feature_image": feature_image,
        "feature_image_alt": feature_image_alt,
        "canonical_url": canonical_url,
        "og_image": og_image,
        "intro_hook": intro_hook,
        "intent_cluster": intent_cluster,
        "approved": False,
        "humanization_verified": False,
        "review_status": "pending",
        "ready_notification_sent": False,
        "external_sources": external_sources,
        "internal_links": internal_links,
    }
    return dump_frontmatter(frontmatter, body)


def main() -> None:
    args = parse_args()
    plan = load_json(Path(args.input))
    drafts_dir = Path(args.output_dir)
    drafts_dir.mkdir(parents=True, exist_ok=True)

    generated = 0
    for idea in plan.get("ideas", []):
        slug = idea["slug"]
        if draft_exists(slug, drafts_dir):
            continue
        markdown_text = build_markdown(idea)
        (drafts_dir / f"{slug}.md").write_text(markdown_text, encoding="utf-8")
        generated += 1
        if generated >= args.max_drafts:
            break

    print(f"Generated drafts: {generated}")


if __name__ == "__main__":
    main()
