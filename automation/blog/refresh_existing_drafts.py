#!/usr/bin/env python3
"""Rewrite existing draft bodies with intent-specific humanized copy."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from draft_io import load_draft, save_draft
from draft_generator import first_sentence
from intent_content import build_body, human_title


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
    if "core-update" in text or "core update" in text:
        return "commercial seo"
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
        cluster = meta.get("intent_cluster") or infer_cluster(str(meta.get("slug", path.stem)), str(meta.get("primary_keyword", "")))
        term = str(meta.get("primary_keyword", "")).replace(" seo strategy", "").strip()
        meta["intent_cluster"] = cluster
        meta["title"] = human_title(term, cluster)
        meta["approved"] = False
        meta["humanization_verified"] = False
        meta["review_status"] = "pending"
        meta["ready_notification_sent"] = False
        idea = {
            "primary_keyword": meta.get("primary_keyword", ""),
            "intent_cluster": cluster,
            "geo_hint": "your service area",
        }
        body = build_body(idea)
        intro_hook = first_sentence(body)
        meta["intro_hook"] = intro_hook
        meta["meta_description"] = (
            f"{intro_hook[:150].rstrip('.')} "
            "Actionable steps for technical SEO, local growth, and AI-era visibility."
        ).strip()
        save_draft(path, meta, body)
        refreshed += 1
        print(f"Refreshed {path.name}")

    print(f"Refreshed drafts: {refreshed}")


if __name__ == "__main__":
    main()
