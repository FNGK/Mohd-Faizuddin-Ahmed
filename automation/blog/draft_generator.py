#!/usr/bin/env python3
"""Generate review-only blog drafts from keyword plan."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


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


def build_markdown(idea: dict) -> str:
    now = datetime.now(timezone.utc).date().isoformat()
    title = idea["title"]
    slug = idea["slug"]
    primary_keyword = idea["primary_keyword"]
    meta_description = f"{title} with practical actions for modern SEO execution across traditional and AI-driven search journeys."
    feature_image = "../../assets/projects/unstop-seo-audit.png"
    feature_image_alt = "SEO strategy implementation visual"
    canonical_url = f"https://fngk.github.io/Mohd-Faizuddin-Ahmed/blog/posts/{slug}.html"
    og_image = "https://fngk.github.io/Mohd-Faizuddin-Ahmed/assets/og/og-default.png"
    external_sources = idea["external_sources"]
    internal_links = idea["internal_links"]
    intro_hook = (
        "Most teams still treat SEO as a ranking-only channel. This guide shows how to combine "
        "technical SEO, AEO, and GEO so visibility maps to qualified pipeline outcomes."
    )

    frontmatter = [
        "---",
        f'title: "{title}"',
        f"slug: {slug}",
        f"date: {now}",
        f'primary_keyword: "{primary_keyword}"',
        f'meta_description: "{meta_description}"',
        f'feature_image: "{feature_image}"',
        f'feature_image_alt: "{feature_image_alt}"',
        f'canonical_url: "{canonical_url}"',
        f'og_image: "{og_image}"',
        f'intro_hook: "{intro_hook}"',
        "approved: false",
        "external_sources:",
        f'  - "{external_sources[0]}"',
        f'  - "{external_sources[1]}"',
        "internal_links:",
        f'  - "{internal_links[0]}"',
        f'  - "{internal_links[1]}"',
        f'  - "{internal_links[2]}"',
        f'  - "{internal_links[3]}"',
        "---",
        "",
    ]

    body = f"""## Why this topic matters now

{primary_keyword} has shifted from a ranking-only conversation to a visibility and trust conversation. Search journeys now move across traditional engines, AI answers, and brand-driven research paths.

Most teams still publish content and expect rankings to carry the entire pipeline. That approach misses how modern users evaluate providers across multiple touchpoints before taking action. A practical strategy must connect discoverability, trust, and conversion design.

## Core strategy model

### 1) Protect technical integrity first

- Keep indexation and crawl behavior stable for your revenue pages.
- Resolve performance blockers that damage user experience and conversion.
- Maintain structured architecture so search systems understand page purpose.

Technical SEO still drives the ceiling for every other channel. If your important pages have crawl friction, duplicate intent, or unstable metadata, no content velocity can compensate.

### 2) Build intent-aligned content systems

- Map each topic to one clear user intent.
- Structure sections for fast scanning and direct answer extraction.
- Add internal links that guide users toward service and decision pages.

Strong content systems are less about volume and more about sequence. Each article should support one stage of decision-making and direct users to the next logical page. This model improves both engagement and conversion quality.

### 3) Build authority signals outside your own site

- Publish case-based insights and practical frameworks.
- Earn relevant mentions and citations from trusted sources.
- Keep author, service, and brand entities consistent across channels.

Authority is a distribution problem and a trust problem. If external references and internal claims are disconnected, answer engines and users both reduce confidence in your content.

## Measurement model for decision-makers

Use KPIs that connect SEO to business outcomes:

- Qualified organic sessions to commercial pages
- Form submissions or calls from SEO landing pages
- Pipeline influence for organic-assisted journeys
- Technical issue resolution velocity

Avoid reporting that only highlights keyword movement without showing lead quality and conversion behavior.

## Execution checklist for the next 30 days

1. Audit technical blockers on key pages.
2. Refresh high-intent pages with direct-answer sections.
3. Update internal links from educational content to commercial pages.
4. Publish one evidence-backed case or framework asset.
5. Track business outcomes, not rankings alone.

## Team alignment notes

Assign clear ownership before implementation starts. SEO, content, and development teams should align on priorities and deadlines, otherwise execution stalls.

Document every recommendation with the expected business impact. This keeps stakeholders aligned and makes reporting more credible.

## Common mistakes to avoid

- Publishing generic content with no unique perspective.
- Using exact-match keywords unnaturally across every paragraph.
- Ignoring conversion pathways on high-traffic pages.
- Claiming outcomes without references or implementation evidence.

## Final recommendation

Treat SEO, AEO, and GEO as one operating system. The strategy should start with technical quality, scale through intent-aligned content, and compound through trusted references and practical conversion pathways.
"""
    return "\n".join(frontmatter) + body


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
