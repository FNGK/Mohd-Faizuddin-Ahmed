#!/usr/bin/env python3
"""Generate keyword and topic ideas from collected trend signals."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gemini_research import (
    GeminiBudget,
    is_gemini_active,
    load_gemini_config,
    maybe_enrich_with_gemini,
    usage_status,
)
from intent_content import human_title
from intent_research import enrich_idea

INTERNAL_LINKS_DEFAULT = [
    "../../services/index.html",
    "../../resources/seo-audit-playbook.html",
    "../../case-studies/index.html",
    "../../contact/index.html",
]

# Wedge-aligned seed keywords. These are phrased the way people actually
# search (AEO/GEO first, then technical/international/local/commercial), so
# they can be used as primary keywords directly — no suffix stapling.
SEED_TERMS = [
    # AEO / GEO wedge (primary focus)
    "answer engine optimization",
    "generative engine optimization",
    "how to rank in ai overviews",
    "how to get cited by chatgpt",
    "ai search optimization",
    "llm seo",
    "schema markup for ai search",
    # Technical
    "technical seo audit",
    "core web vitals optimization",
    "google core update recovery",
    # International (positioning)
    "international seo best practices",
    "hreflang implementation",
    # Local + commercial
    "local seo for service businesses",
    "saas seo strategy",
    "how much does seo cost",
]

BLOCKED_TERMS = {
    "sejournal",
    "website",
    "searchenginejournal",
    "google",
    "search",
    "guide",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build keyword plan from trends JSON.")
    parser.add_argument(
        "--input",
        default="automation/blog/data/trends.json",
        help="Trends JSON path",
    )
    parser.add_argument(
        "--output",
        default="automation/blog/data/keyword_plan.json",
        help="Keyword plan output path",
    )
    parser.add_argument("--max-ideas", type=int, default=8, help="Maximum idea count")
    parser.add_argument(
        "--gemini",
        action="store_true",
        help="Allow Gemini enrichment (still respects max calls and cache)",
    )
    parser.add_argument(
        "--no-gemini",
        action="store_true",
        help="Disable Gemini for this run",
    )
    return parser.parse_args()


def slugify(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9\s-]", "", text).strip().lower()
    text = re.sub(r"\s+", "-", text)
    return re.sub(r"-{2,}", "-", text)[:72].strip("-")


def build_title_from_term(term: str) -> str:
    return human_title(term, classify_intent(term))


_QUESTION_PREFIX = re.compile(
    r"^(how to|how do i|what is|what are|why|when to|where to)\s+", re.IGNORECASE
)


def build_keywords(term: str) -> tuple[str, list[str]]:
    """Build a realistic primary keyword and natural secondary variants.

    The previous version appended " seo strategy" to every term, producing
    malformed, zero-volume queries (e.g. "seo reporting for pipeline seo
    strategy"). We now use the cleaned term itself as the primary keyword
    (including valid question-form queries like "how to rank in ai overviews")
    and derive grammatical, search-like long-tail variants from the topic stem
    — so noun-phrase seeds never become "how to technical seo audit".
    """
    primary = re.sub(r"\s+", " ", term).strip().lower()
    # Strip a leading question phrase so modifiers attach to a clean noun stem.
    stem = _QUESTION_PREFIX.sub("", primary).strip() or primary
    candidates = [
        f"{stem} checklist",
        f"{stem} examples",
        f"{stem} best practices",
        f"{stem} 2026",
    ]
    secondary: list[str] = []
    seen = {primary}
    for variant in candidates:
        variant = re.sub(r"\s+", " ", variant).strip()
        if variant and variant not in seen:
            seen.add(variant)
            secondary.append(variant)
        if len(secondary) >= 3:
            break
    return primary, secondary


def classify_intent(term: str) -> str:
    if any(t in term for t in ("local", "map", "profile", "gbp", "near me")):
        return "local growth"
    if any(
        t in term
        for t in (
            "ai",
            "llm",
            "answer",
            "generative",
            "chatgpt",
            "gpt",
            "aeo",
            "geo",
            "overview",
            "cited",
        )
    ):
        return "aeo and geo"
    if any(t in term for t in ("core", "crawl", "index", "technical", "schema", "audit", "hreflang", "core web vitals")):
        return "technical optimization"
    return "commercial seo"


def load_trends(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Trends file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    trends = load_trends(input_path)
    dynamic_terms = [
        t["term"]
        for t in trends.get("top_terms", [])
        if len(t["term"]) > 4 and t["term"] not in BLOCKED_TERMS
    ]
    top_terms = SEED_TERMS + dynamic_terms
    source_entries = trends.get("entries", [])

    ideas = []
    seen_slugs = set()
    source_cursor = 0
    trend_titles = [e.get("title", "") for e in source_entries[:12]]

    cfg = load_gemini_config()
    gemini_on = is_gemini_active(cfg) and not args.no_gemini
    if args.gemini:
        cfg = dict(cfg)
        cfg["gemini_enabled"] = True
        gemini_on = not args.no_gemini
    budget = GeminiBudget(int(cfg.get("gemini_max_calls_per_run", 1)) if gemini_on else 0)
    gemini_calls = 0
    gemini_skipped_quota = False
    if gemini_on:
        print(f"Gemini: {usage_status(cfg)}")

    for term in top_terms:
      # Use selected terms only.
        title = build_title_from_term(term)
        slug = slugify(title)
        if not slug or slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        primary_keyword, secondary_keywords = build_keywords(term)

        sources = []
        while len(sources) < 2 and source_cursor < len(source_entries):
            sources.append(source_entries[source_cursor]["url"])
            source_cursor += 1
        if len(sources) < 2:
            sources.extend(
                [
                    "https://developers.google.com/search/docs/fundamentals/creating-helpful-content",
                    "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data",
                ][: 2 - len(sources)]
            )

        idea = enrich_idea(
            {
                "title": title,
                "slug": slug,
                "primary_keyword": primary_keyword,
                "secondary_keywords": secondary_keywords,
                "intent_cluster": classify_intent(term),
                "target_audience": "Marketing leads, founders, and growth managers",
                "cta": "Book a strategy call",
                "external_sources": sources,
                "internal_links": INTERNAL_LINKS_DEFAULT,
                "recommended_word_count": 1200,
            },
            term,
            trend_titles,
        )
        if gemini_on and not gemini_skipped_quota:
            idea, used = maybe_enrich_with_gemini(idea, term, trend_titles, budget=budget)
            if used:
                gemini_calls += 1
            elif idea.pop("gemini_quota_paused", None):
                gemini_skipped_quota = True
                print("Gemini free-tier quota hit — heuristic research only until cooldown.")
        ideas.append(idea)
        if len(ideas) >= args.max_ideas:
            break

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "idea_count": len(ideas),
        "gemini_calls_this_run": gemini_calls,
        "gemini_enabled": gemini_on,
        "ideas": ideas,
    }
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    gemini_note = f", Gemini API calls: {gemini_calls}" if gemini_on else ""
    print(f"Wrote keyword plan: {output_path} ({len(ideas)} ideas{gemini_note})")


if __name__ == "__main__":
    main()
