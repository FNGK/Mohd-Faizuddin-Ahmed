"""Build long-form draft bodies with in-body links and strict word-count bounds."""

from __future__ import annotations

import re
from typing import Any

from content_config import (
    DEFAULT_RECOMMENDED_WORD_COUNT,
    WORD_COUNT_BUFFER_ABOVE,
    WORD_COUNT_MAX_ABOVE,
)
from intent_content import (
    _body_aeo_geo,
    _body_core_update,
    _body_generic,
    _body_local_growth,
    _body_technical,
)
from readability import count_words

WORD_RE = re.compile(r"\b\w+\b")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

INTERNAL_SPECS: list[tuple[str, list[str]]] = [
    ("../../services/technical-seo.html", ["technical SEO program", "crawl and indexation fixes"]),
    ("../../services/local-seo.html", ["local SEO and Maps growth", "location-led visibility"]),
    ("../../services/content-seo.html", ["content SEO and topical authority", "editorial SEO support"]),
    ("../../case-studies/index.html", ["documented SEO case studies", "client results archive"]),
    ("../../resources/seo-audit-playbook.html", ["SEO audit playbook", "structured audit framework"]),
    ("../../contact/index.html", ["strategy call", "book a working session"]),
    ("../../free-tools/gsc-error-priority-calculator.html", ["GSC error prioritization tool", "Search Console triage calculator"]),
]

EXPANSION_PARAGRAPHS: list[str] = [
    (
        "When you align search, answer engines, and on-site experience, you'll reduce bounce from mismatched "
        "intent. You'll improve qualified pipeline if you review Search Console weekly. Note which templates "
        "earn clicks but lose users on mobile—those URLs are your highest-leverage SXO fixes."
    ),
    (
        "Stakeholders rarely need another keyword list; they need a prioritized queue tied to revenue. "
        "Document assumptions before each release, then compare impressions, CTR, and form starts so "
        "you can explain what changed without guessing after algorithm updates."
    ),
    (
        "Generative surfaces reward pages that state limits, timelines, and prerequisites in plain language. "
        "If a paragraph could apply to any competitor, rewrite it with a process detail only your team "
        "would know from delivery work."
    ),
    (
        "Internal linking should reinforce the buyer journey: awareness content points to proof, proof "
        "points to services, and services point to a single conversion path. Avoid orphan posts that "
        "never reference how you actually implement the advice."
    ),
]


def word_bounds(recommended: int) -> tuple[int, int]:
    return recommended + WORD_COUNT_BUFFER_ABOVE, recommended + WORD_COUNT_MAX_ABOVE


def _cluster_body(idea: dict[str, Any]) -> str:
    cluster = (idea.get("intent_cluster") or "").strip().lower()
    builders = {
        "local growth": _body_local_growth,
        "technical optimization": _body_technical,
        "aeo and geo": _body_aeo_geo,
        "commercial seo": _body_core_update,
    }
    builder = builders.get(cluster, _body_generic)
    return builder(idea)


def _serp_research_section(idea: dict[str, Any]) -> str:
    kw = idea.get("primary_keyword", "seo strategy")
    analysis = idea.get("serp_analysis", "")
    intent = idea.get("serp_intent", "informational")
    funnel = idea.get("funnel_stage", "awareness")
    features = ", ".join(idea.get("serp_features", []))
    return f"""## What SERP and audience research shows

{analysis}

For **{kw}**, you're targeting **{intent}** intent at the **{funnel}** stage. Give scanners a direct answer first. Give evaluators proof mid-page. Give decision-makers one clear next step. SERP features to design for: {features}.

Last reviewed: {idea.get("date", "2026")}. We follow Google Search Essentials, spam policies, and helpful-content guidance."""


def _paa_faq_section(idea: dict[str, Any]) -> str:
    questions: list[str] = list(idea.get("paa_questions") or [])[:6]
    kw = str(idea.get("primary_keyword", "seo"))
    blocks = ["## People also ask (PAA) — answered for search and AI surfaces", ""]
    for q in questions:
        blocks.append(f"### {q}")
        blocks.append(
            f"You'll want one URL you control for this question. Answer in two short sentences first. "
            f"Then add steps and limits. For **{kw}**, use Search Console, call notes, and shipped fixes. "
            f"Don't speculate—link to primary docs when you can't verify a claim."
        )
        blocks.append("")
    return "\n".join(blocks).strip()


def _sxo_section(idea: dict[str, Any]) -> str:
    cta = idea.get("cta", "Book a strategy call")
    return f"""## Search experience (SXO) checklist on this page

- **Scan path:** headings mirror real queries; the first screen states outcome, audience, and constraint.
- **Trust:** author box, dated review, and links to services and proof—not generic widgets alone.
- **Action:** one primary CTA ({cta}) repeated after proof, not competing buttons with equal weight.
- **Performance:** prioritize LCP and INP on templates that receive organic entries from this topic.
- **Accessibility:** descriptive link text, sufficient contrast, and headings that do not skip levels.
- **Proof:** one case-led example above the fold on money pages.
- **Speed:** fix LCP on the top three organic landing templates.
- **Forms:** one primary CTA; remove duplicate buttons with equal weight.
- **Measurement:** track qualified actions weekly, not rank checks alone.

If mobile scroll depth drops before the FAQ block, move the strongest proof higher and shorten paragraphs."""


def _pick_internal_links(count: int) -> list[tuple[str, str]]:
    picked: list[tuple[str, str]] = []
    for idx, (url, anchors) in enumerate(INTERNAL_SPECS):
        if len(picked) >= count:
            break
        picked.append((url, anchors[idx % len(anchors)]))
    return picked


def _pick_external_links(idea: dict[str, Any], count: int) -> list[tuple[str, str]]:
    urls = list(idea.get("external_sources") or [])
    labels = [
        "industry analysis",
        "search engine documentation",
        "publisher research",
        "official guidance",
    ]
    out: list[tuple[str, str]] = []
    for idx, url in enumerate(urls[:count]):
        out.append((url, labels[idx % len(labels)]))
    while len(out) < count:
        out.append(
            (
                "https://developers.google.com/search/docs/fundamentals/creating-helpful-content",
                "Google helpful content guidance",
            )
        )
    return out[:count]


def _weave_links(body: str, idea: dict[str, Any]) -> str:
    internals = _pick_internal_links(4)
    externals = _pick_external_links(idea, 3)
    paragraphs = [p.strip() for p in re.split(r"\n\n+", body) if p.strip()]
    if len(paragraphs) < 6:
        return body

    insert_at = [2, 4, 6, 8, 10, 12, 14, 16]
    link_idx = 0
    for pos in insert_at:
        if link_idx >= len(internals) + len(externals):
            break
        if pos >= len(paragraphs):
            break
        para = paragraphs[pos]
        if para.startswith("#"):
            continue
        if MD_LINK_RE.search(para):
            continue
        if link_idx < len(internals):
            url, anchor = internals[link_idx]
            sentence = f" If you want help implementing this, see our [{anchor}]({url})."
            link_idx += 1
        else:
            ext_i = link_idx - len(internals)
            url, anchor = externals[min(ext_i, len(externals) - 1)]
            sentence = f" For independent context, see [{anchor}]({url})."
            link_idx += 1
        if not para.endswith("."):
            para += "."
        paragraphs[pos] = para + sentence

    return "\n\n".join(paragraphs)


def _trim_to_max_words(text: str, max_words: int) -> str:
    marker = "## Sources and further reading"
    sources_block = ""
    main = text.strip()
    if marker in main:
        main, sources_block = main.split(marker, 1)
        sources_block = marker + sources_block

    paragraphs = [p.strip() for p in re.split(r"\n\n+", main.strip()) if p.strip()]
    reserved = count_words(sources_block) if sources_block else 0
    budget = max(200, max_words - reserved)

    while paragraphs and count_words("\n\n".join(paragraphs)) > budget:
        paragraphs.pop()
    body = "\n\n".join(paragraphs)
    if sources_block:
        body = f"{body}\n\n{sources_block.strip()}".strip()
    if count_words(body) <= max_words:
        return body
    return _trim_to_max_words(body.replace(sources_block, "").strip(), max_words) if sources_block else body


def _append_source_links_section(body: str, idea: dict[str, Any]) -> str:
    externals = _pick_external_links(idea, 4)
    lines = ["## Sources and further reading", ""]
    for url, anchor in externals[:4]:
        lines.append(
            f"You'll find useful context in [{anchor}]({url})—use it to corroborate claims, not to copy text."
        )
    section = "\n\n".join(lines)
    return f"{body}\n\n{section}".strip() if body else section


def _pad_to_min_words(text: str, min_words: int, idea: dict[str, Any]) -> str:
    body = text
    i = 0
    while count_words(body) < min_words:
        para = EXPANSION_PARAGRAPHS[i % len(EXPANSION_PARAGRAPHS)]
        funnel = idea.get("funnel_stage", "consideration")
        cluster = idea.get("intent_cluster", "seo")
        body += (
            f"\n\n## Operational note for {funnel} readers\n\n"
            f"{para} This aligns with your **{cluster}** focus and keeps claims tied to processes you can audit."
        )
        i += 1
        if i > 12:
            break
    return body


def _quick_answer_block(idea: dict[str, Any]) -> str:
    kw = idea.get("primary_keyword", "seo strategy")
    funnel = idea.get("funnel_stage", "consideration")
    return f"""## Quick answer

You're working on **{kw}** at the **{funnel}** stage. Don't chase every tactic at once. Fix one money page, add proof, and link to services you actually sell.

- Pick one money URL and one technical blocker.
- Add proof above the fold on that URL.
- Link to a relevant service page in context.
- Measure qualified leads weekly.
- Review Search Console for intent drift.

You'll know it's working when qualified leads rise—not when a rank tracker turns green."""


def build_body(idea: dict[str, Any]) -> str:
    recommended = int(idea.get("recommended_word_count") or DEFAULT_RECOMMENDED_WORD_COUNT)
    min_w, max_w = word_bounds(recommended)

    core_sections = [
        _quick_answer_block(idea),
        _serp_research_section(idea),
        _cluster_body(idea),
        _paa_faq_section(idea),
    ]
    tail_sections = [_sxo_section(idea)]
    body = "\n\n".join(core_sections)
    body = _weave_links(body, idea)
    body = _pad_to_min_words(body, min_w, idea)
    if count_words(body) > max_w:
        body = _trim_to_max_words(body, max_w)
    if count_words(body) < min_w:
        body = _pad_to_min_words(body, min_w, idea)
    body = _polish_long_sentences(body)
    reserved = "\n\n".join(tail_sections)
    reserved += "\n\n" + _append_source_links_section("", idea).strip()
    budget = max(200, max_w - count_words(reserved))
    if count_words(body) > budget:
        body = _trim_to_max_words(body, budget)
    body = f"{body.strip()}\n\n{reserved.strip()}".strip()
    if count_words(body) > max_w:
        body = _trim_to_max_words(body, max_w)
    return body.strip() + "\n"


def _polish_long_sentences(text: str) -> str:
    """Split very long sentences to improve readability scores without changing meaning much."""
    out_blocks: list[str] = []
    for block in re.split(r"\n\n+", text.strip()):
        if block.startswith("#") or "](" in block:
            out_blocks.append(block)
            continue
        sentences = re.split(r"(?<=[.!?])\s+", block)
        polished: list[str] = []
        for sentence in sentences:
            words = sentence.split()
            if len(words) > 26:
                mid = len(words) // 2
                polished.append(" ".join(words[:mid]).rstrip(",;") + ".")
                polished.append(" ".join(words[mid:]))
            else:
                polished.append(sentence)
        out_blocks.append(" ".join(polished))
    return "\n\n".join(out_blocks)
