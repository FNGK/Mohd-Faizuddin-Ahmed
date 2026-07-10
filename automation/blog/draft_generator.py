#!/usr/bin/env python3
"""Generate review-only blog drafts from keyword plan."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from content_config import (
    META_DESC_LEN_MAX,
    META_DESC_LEN_MIN,
    TITLE_LEN_MAX,
    TITLE_LEN_MIN,
)
from draft_io import dump_frontmatter
from intent_content import build_body, human_title, smart_title_case


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
    for block in text.split("\n\n"):
        block = block.strip()
        if not block or block.startswith("#"):
            continue
        for line in block.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                parts = re.split(r"(?<=[.!?])\s+", stripped)
                return parts[0] if parts else stripped
    return "Practical guidance for teams that need search visibility tied to pipeline outcomes."


def build_seo_title(idea: dict, term: str, intent_cluster: str, primary_keyword: str) -> str:
    """Prefer the well-formed title keyword_planner already built via human_title().

    The previous version discarded that title unconditionally and rebuilt one from
    only the first three primary_keyword tokens (e.g. "how to get cited by chatgpt"
    -> "How To Get"), which routinely landed under the 35-char minimum and dropped
    the actual meaningful keyword tokens ("cited", "chatgpt")—so titles both failed
    length checks and failed "primary keyword missing from title" checks.
    """
    base = str(idea.get("title") or human_title(term, intent_cluster)).strip()
    kw_tokens = [t for t in primary_keyword.lower().split() if len(t) > 3 and t not in {"strategy"}]

    def covers_keyword(title: str) -> bool:
        low = title.lower()
        return not kw_tokens or all(t in low for t in kw_tokens[:2])

    def in_bounds(title: str) -> bool:
        return TITLE_LEN_MIN <= len(title) <= TITLE_LEN_MAX

    if in_bounds(base) and covers_keyword(base):
        return base

    # Fallback: rebuild from the full keyword phrase (acronym-aware via
    # smart_title_case) instead of a truncated 3-token label.
    candidate = human_title(primary_keyword, intent_cluster)
    if in_bounds(candidate) and covers_keyword(candidate):
        return candidate

    label = smart_title_case(primary_keyword) or term.title()
    candidate = f"{label}: A 2026 Playbook for Search Teams"
    if len(candidate) > TITLE_LEN_MAX:
        candidate = candidate[:TITLE_LEN_MAX].rsplit(" ", 1)[0]
    while len(candidate) < TITLE_LEN_MIN:
        candidate += " Now"
    return candidate


def build_meta_description(intro: str, primary_keyword: str) -> str:
    base = re.sub(r"\*+", "", intro).strip()
    if len(base) > 90:
        base = base[:87].rsplit(" ", 1)[0] + "…"
    suffix = f" {primary_keyword.strip()} — SERP-aligned SEO, AEO, GEO, and SXO steps."
    meta = (base + suffix).strip()
    if len(meta) > META_DESC_LEN_MAX:
        meta = meta[: META_DESC_LEN_MAX - 1].rsplit(" ", 1)[0] + "…"
    while len(meta) < META_DESC_LEN_MIN:
        meta += " Actionable for marketing leaders."
        if len(meta) > META_DESC_LEN_MAX:
            meta = meta[:META_DESC_LEN_MAX]
            break
    return meta


def build_markdown(idea: dict) -> str:
    now = datetime.now(timezone.utc).date().isoformat()
    idea = dict(idea)
    idea["date"] = now
    intent_cluster = idea.get("intent_cluster", "commercial seo")
    term = str(idea.get("primary_keyword", "")).replace(" seo strategy", "").strip() or idea.get("slug", "seo")
    slug = idea["slug"]
    primary_keyword = idea["primary_keyword"]
    title = build_seo_title(idea, term, intent_cluster, primary_keyword)
    body = build_body(idea)
    intro_hook = first_sentence(body)
    meta_description = build_meta_description(intro_hook, primary_keyword)
    feature_image = "../../assets/projects/unstop-seo-audit.png"
    feature_image_alt = f"{title} — SEO With Faiz editorial illustration"
    canonical_url = f"https://seowithfaiz.com/blog/posts/{slug}.html"
    og_image = "https://seowithfaiz.com/assets/og/og-default.png"

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
        "serp_intent": idea.get("serp_intent"),
        "funnel_stage": idea.get("funnel_stage"),
        "serp_features": idea.get("serp_features", []),
        "paa_questions": idea.get("paa_questions", []),
        "serp_analysis": idea.get("serp_analysis"),
        "recommended_word_count": idea.get("recommended_word_count", 1200),
        "target_audience": idea.get("target_audience"),
        "cta": idea.get("cta", "Book a strategy call"),
        "approved": False,
        "editorial_reviewed": False,
        "humanization_verified": False,
        "review_status": "pending",
        "ready_notification_sent": False,
        "external_sources": idea["external_sources"],
        "internal_links": idea["internal_links"],
        "research_source": idea.get("research_source", "heuristic"),
        "gemini_enriched": bool(idea.get("gemini_enriched")),
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
