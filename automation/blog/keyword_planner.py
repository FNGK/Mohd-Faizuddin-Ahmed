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

from intent_content import human_title

INTERNAL_LINKS_DEFAULT = [
    "../../services/index.html",
    "../../resources/seo-audit-playbook.html",
    "../../case-studies/index.html",
    "../../contact/index.html",
]

SEED_TERMS = [
    "ai search visibility",
    "google core update recovery",
    "local seo conversion strategy",
    "technical seo prioritization",
    "seo reporting for pipeline",
    "entity seo strategy",
    "international seo localization",
    "programmatic seo quality control",
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
    return parser.parse_args()


def slugify(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9\s-]", "", text).strip().lower()
    text = re.sub(r"\s+", "-", text)
    return re.sub(r"-{2,}", "-", text)[:72].strip("-")


def build_title_from_term(term: str) -> str:
    return human_title(term, classify_intent(term))


def classify_intent(term: str) -> str:
    if any(t in term for t in ("local", "map", "profile")):
        return "local growth"
    if any(t in term for t in ("ai", "llm", "answer", "generative")):
        return "aeo and geo"
    if any(t in term for t in ("core", "crawl", "index", "technical", "schema")):
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

    for term in top_terms:
      # Use selected terms only.
        title = build_title_from_term(term)
        slug = slugify(title)
        if not slug or slug in seen_slugs:
            continue
        seen_slugs.add(slug)

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

        ideas.append(
            {
                "title": title,
                "slug": slug,
                "primary_keyword": f"{term} seo strategy",
                "secondary_keywords": [
                    f"{term} seo checklist",
                    f"{term} best practices",
                    f"{term} implementation guide",
                ],
                "intent_cluster": classify_intent(term),
                "target_audience": "Marketing leads, founders, and growth managers",
                "cta": "Book a strategy call",
                "external_sources": sources,
                "internal_links": INTERNAL_LINKS_DEFAULT,
                "recommended_word_count": 1200,
            }
        )
        if len(ideas) >= args.max_ideas:
            break

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "idea_count": len(ideas),
        "ideas": ideas,
    }
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    print(f"Wrote keyword plan: {output_path} ({len(ideas)} ideas)")


if __name__ == "__main__":
    main()
