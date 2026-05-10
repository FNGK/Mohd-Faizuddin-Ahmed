#!/usr/bin/env python3
"""Collect SEO trend headlines from trusted RSS feeds."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import feedparser

FEEDS = [
    ("Google Search Central", "https://developers.google.com/search/blog/rss.xml"),
    ("Search Engine Journal", "https://www.searchenginejournal.com/feed/"),
    ("Search Engine Land", "https://searchengineland.com/feed"),
    ("Moz", "https://moz.com/blog/feed"),
]

STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "into", "your", "you",
    "will", "what", "when", "where", "how", "about", "guide", "2026", "2025",
    "seo", "google", "search", "update", "latest", "news"
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect trend signals from SEO feeds.")
    parser.add_argument(
        "--output",
        default="automation/blog/data/trends.json",
        help="Output JSON path",
    )
    parser.add_argument("--max-items", type=int, default=40, help="Maximum articles to keep")
    return parser.parse_args()


def normalize_tokens(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z\-]{2,}", text.lower())
    return [w for w in words if w not in STOPWORDS]


def collect(max_items: int) -> tuple[list[dict], list[dict]]:
    entries: list[dict] = []
    keyword_counter: Counter[str] = Counter()

    for source_name, feed_url in FEEDS:
        parsed = feedparser.parse(feed_url)
        for item in parsed.entries[:15]:
            title = (item.get("title") or "").strip()
            link = (item.get("link") or "").strip()
            published = (
                item.get("published")
                or item.get("updated")
                or datetime.now(timezone.utc).isoformat()
            )
            if not title or not link:
                continue

            tokens = normalize_tokens(title)
            keyword_counter.update(tokens)
            entries.append(
                {
                    "source": source_name,
                    "title": title,
                    "url": link,
                    "published": published,
                    "tokens": tokens[:8],
                }
            )

    # Deduplicate by URL while preserving insertion order.
    seen = set()
    deduped = []
    for entry in entries:
        if entry["url"] in seen:
            continue
        seen.add(entry["url"])
        deduped.append(entry)
        if len(deduped) >= max_items:
            break

    top_terms = [{"term": term, "count": count} for term, count in keyword_counter.most_common(40)]
    return deduped, top_terms


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    entries, top_terms = collect(args.max_items)
    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "feeds": [f[0] for f in FEEDS],
        "entry_count": len(entries),
        "entries": entries,
        "top_terms": top_terms,
    }
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    print(f"Wrote trends: {output_path} ({len(entries)} entries)")


if __name__ == "__main__":
    main()
