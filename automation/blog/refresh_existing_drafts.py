#!/usr/bin/env python3
"""Rewrite existing draft bodies with research-backed, compliance-ready copy."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from draft_generator import build_meta_description, first_sentence
from draft_io import load_draft, save_draft
from intent_content import build_body, human_title
from intent_research import enrich_idea


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh draft bodies and titles.")
    parser.add_argument("--drafts-dir", default="blog/drafts", help="Draft folder path")
    return parser.parse_args()


def infer_cluster(slug: str, keyword: str) -> str:
    text = f"{slug} {keyword}".lower()
    if "local" in text:
        return "local growth"
    if any(token in text for token in ("ai-search", "ai search", "visibility", "aeo", "geo")):
        return "aeo and geo"
    if any(token in text for token in ("technical", "crawl", "index", "schema")):
        return "technical optimization"
    return "commercial seo"


def main() -> None:
    args = parse_args()
    drafts_dir = Path(args.drafts_dir)
    if not drafts_dir.exists():
        print("No drafts directory found.")
        return

    refreshed = 0
    for path in sorted(drafts_dir.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        meta, _ = load_draft(path)
        cluster = meta.get("intent_cluster") or infer_cluster(
            str(meta.get("slug", path.stem)), str(meta.get("primary_keyword", ""))
        )
        term = str(meta.get("primary_keyword", "")).replace(" seo strategy", "").strip()
        meta["intent_cluster"] = cluster
        meta["title"] = human_title(term, cluster)
        meta["approved"] = False
        meta["editorial_reviewed"] = False
        meta["humanization_verified"] = False
        meta["review_status"] = "pending"
        meta["ready_notification_sent"] = False
        idea = enrich_idea(
            {
                "primary_keyword": meta.get("primary_keyword", ""),
                "intent_cluster": cluster,
                "geo_hint": "your service area",
                "external_sources": meta.get("external_sources", []),
                "recommended_word_count": meta.get("recommended_word_count", 1200),
                "date": meta.get("date"),
            },
            term,
        )
        for key in ("serp_intent", "funnel_stage", "serp_features", "paa_questions", "serp_analysis"):
            meta[key] = idea.get(key)
        meta["recommended_word_count"] = idea.get("recommended_word_count", 1200)
        body = build_body(idea)
        intro_hook = first_sentence(body)
        meta["intro_hook"] = intro_hook
        meta["meta_description"] = build_meta_description(intro_hook, str(meta.get("primary_keyword", "")))
        save_draft(path, meta, body)
        refreshed += 1
        print(f"Refreshed {path.name}")

    print(f"Refreshed drafts: {refreshed}")


if __name__ == "__main__":
    main()
