"""SEO, AEO/GEO, SXO, readability, policy, and linking compliance checks."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from content_config import (
    HUMANIZATION_SCORE_MIN,
    META_DESC_LEN_MAX,
    META_DESC_LEN_MIN,
    MIN_BULLET_LINES,
    MIN_EXTERNAL_LINKS_IN_BODY,
    MIN_H2_SECTIONS,
    MIN_H3_SECTIONS,
    MIN_INTERNAL_LINKS_IN_BODY,
    ORIGINALITY_SCORE_MIN,
    TITLE_LEN_MAX,
    TITLE_LEN_MIN,
    WORD_COUNT_BUFFER_ABOVE,
    WORD_COUNT_MAX_ABOVE,
)
from readability import ReadabilityReport, count_words, evaluate_readability

MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
GENERIC_ANCHORS = {"click here", "read more", "learn more", "here", "this link"}

POLICY_BANNED_PHRASES = [
    "guaranteed #1",
    "guaranteed rank",
    "instant rankings",
    "secret google trick",
    "google will never know",
    "manipulate google",
    "buy backlinks cheap",
    "pbn",
    "cloaking",
    "keyword stuffing",
]

POLICY_RISKY_UNVERIFIED = [
    "100% guaranteed",
    "never fails",
    "always ranks",
    "google confirmed you will rank",
]

YMYL_TRIGGERS = [
    "medical advice",
    "legal advice",
    "investment guarantee",
    "cure ",
    "prescription",
]


@dataclass
class ComplianceReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return not self.errors


def _body_links(body: str) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    internal: list[tuple[str, str]] = []
    external: list[tuple[str, str]] = []
    for anchor, url in MD_LINK_RE.findall(body):
        anchor_l = anchor.strip().lower()
        if url.startswith("http"):
            external.append((anchor, url))
        else:
            internal.append((anchor, url))
    return internal, external


def validate_word_count(body: str, recommended: int) -> list[str]:
    errors = []
    min_w = recommended + WORD_COUNT_BUFFER_ABOVE
    max_w = recommended + WORD_COUNT_MAX_ABOVE
    wc = count_words(body)
    if wc <= recommended:
        errors.append(f"Word count {wc} must be above recommended {recommended}.")
    if wc < min_w:
        errors.append(f"Word count {wc} below minimum {min_w} (recommended+{WORD_COUNT_BUFFER_ABOVE}).")
    if wc > max_w:
        errors.append(f"Word count {wc} exceeds maximum {max_w} (recommended+{WORD_COUNT_MAX_ABOVE}).")
    return errors


def validate_seo(data: dict[str, Any], body: str) -> list[str]:
    errors = []
    title = str(data.get("title", ""))
    meta = str(data.get("meta_description", ""))
    kw = str(data.get("primary_keyword", "")).strip().lower()
    slug = str(data.get("slug", ""))

    if not (TITLE_LEN_MIN <= len(title) <= TITLE_LEN_MAX):
        errors.append(f"Title length {len(title)}; require {TITLE_LEN_MIN}–{TITLE_LEN_MAX} characters.")
    if not (META_DESC_LEN_MIN <= len(meta) <= META_DESC_LEN_MAX):
        errors.append(f"Meta description length {len(meta)}; require {META_DESC_LEN_MIN}–{META_DESC_LEN_MAX}.")
    if kw:
        core_tokens = [t for t in kw.split() if len(t) > 3 and t not in {"strategy"}]
        if core_tokens and not all(t in title.lower() for t in core_tokens[:2]):
            errors.append("Primary keyword missing from title.")
    if kw and kw not in meta.lower():
        errors.append("Primary keyword missing from meta description.")
    if kw:
        first_chunk = body.lower()[:800]
        if kw not in first_chunk:
            errors.append("Primary keyword missing from opening content.")
    if slug and slug not in str(data.get("canonical_url", "")):
        errors.append("Canonical URL does not include slug.")
    if not data.get("canonical_url", "").startswith("https://seowithfaiz.com/"):
        errors.append("Canonical must use https://seowithfaiz.com/ production domain.")
    if len(re.findall(r"^##\s+", body, flags=re.MULTILINE)) < MIN_H2_SECTIONS:
        errors.append(f"Need at least {MIN_H2_SECTIONS} H2 sections.")
    if len(re.findall(r"^###\s+", body, flags=re.MULTILINE)) < MIN_H3_SECTIONS:
        errors.append(f"Need at least {MIN_H3_SECTIONS} H3 sections (PAA/FAQ).")
    if len(re.findall(r"^\s*-\s+", body, flags=re.MULTILINE)) < MIN_BULLET_LINES:
        errors.append(f"Need at least {MIN_BULLET_LINES} bullet lines for scannability.")
    return errors


AIO_SURFACES = (
    "chatgpt", "perplexity", "ai overview", "ai overviews", "ai mode",
    "gemini", "copilot", "claude", "google's ai",
)


def validate_aeo_geo(data: dict[str, Any], body: str) -> list[str]:
    errors = []
    if "people also ask" not in body.lower() and "frequently asked questions" not in body.lower():
        errors.append("Missing PAA/FAQ section for AEO/GEO.")
    paa_count = len(data.get("paa_questions") or [])
    if paa_count < 4:
        errors.append("Need at least 4 PAA questions in frontmatter research.")
    if "last reviewed" not in body.lower():
        errors.append("Missing 'Last reviewed' freshness signal for answer engines.")
    if not re.search(r"\*\*[^*]+\*\*", body):
        errors.append("Need bold entity or key-term markers for extractable answers.")
    if "schema" not in body.lower() and "structured data" not in body.lower():
        errors.append("Reference structured data/schema for GEO corroboration.")
    return errors


def validate_aio(body: str) -> list[str]:
    """AIO: the piece must name a real AI answer surface, not just say "AI interfaces".

    Naming ChatGPT/Perplexity/AI Overviews/Gemini/Copilot specifically is both more
    truthful (real, checkable products vs. vague hand-waving) and a stronger signal
    that the content was written to be citable on those surfaces, not just SEO copy
    with "AI" sprinkled in.
    """
    errors = []
    lower = body.lower()
    if not any(surface in lower for surface in AIO_SURFACES):
        errors.append(
            "Name at least one concrete AI answer surface (ChatGPT, Perplexity, Google AI "
            "Overviews, Gemini, or Copilot) for AIO—generic 'AI interfaces' language doesn't count."
        )
    return errors


_INTENT_STOPWORDS = {
    "what", "when", "where", "which", "while", "with", "your", "that", "this",
    "does", "will", "have", "from", "into", "about", "their", "there", "these",
    "those", "than", "then", "just", "much", "many", "most", "some", "such",
}


def validate_user_intent(body: str, data: dict[str, Any]) -> list[str]:
    """The reader (and an AI crawler skimming the first screen) must instantly see
    what this piece is for and who it's for—and every FAQ/PAA answer must actually
    answer the question asked, not recite a generic template. Catches the exact
    failure mode where an article scored well on every metric except being useful:
    identical boilerplate under six different questions.
    """
    errors = []
    lead = body.strip()[:600].lower()
    if not any(marker in lead for marker in ("quick answer", "tl;dr", "short answer", "in short")):
        errors.append(
            "Opening must lead with a quick-answer/TL;DR framing in the first screen so "
            "intent is obvious immediately—not just eventually."
        )
    if not str(data.get("target_audience") or "").strip():
        errors.append("Missing target_audience — content must be written for a specific reader, not 'everyone'.")

    for match in re.finditer(r"^###\s+(.+)$\n+([^#]+)", body, flags=re.MULTILINE):
        question, answer = match.group(1), match.group(2)
        q_words = {
            w for w in re.findall(r"[a-z']{4,}", question.lower())
            if w not in _INTENT_STOPWORDS
        }
        a_words = set(re.findall(r"[a-z']{4,}", answer.lower()))
        if q_words and not (q_words & a_words):
            errors.append(
                f"FAQ answer for '{question[:60]}' doesn't reference the question's own "
                "terms—looks like a generic template, not a real answer."
            )
    return errors


def validate_sxo(body: str, data: dict[str, Any]) -> list[str]:
    errors = []
    if "## Search experience (SXO)" not in body:
        errors.append("Missing SXO checklist section.")
    if "book a strategy call" not in body.lower() and "strategy call" not in body.lower():
        errors.append("Missing clear conversion CTA language (SXO).")
    long_paras = [p for p in body.split("\n\n") if count_words(p) > 120 and not p.startswith("#")]
    if long_paras:
        errors.append(f"{len(long_paras)} paragraph(s) exceed 120 words; break up for mobile scan.")
    if "?" not in body:
        errors.append("Include at least one reader question for engagement/SXO.")
    funnel = data.get("funnel_stage")
    if not funnel:
        errors.append("Missing funnel_stage in research metadata.")
    return errors


def validate_links(body: str) -> list[str]:
    errors = []
    internal, external = _body_links(body)
    if len(internal) < MIN_INTERNAL_LINKS_IN_BODY:
        errors.append(
            f"Need {MIN_INTERNAL_LINKS_IN_BODY}+ internal markdown links in body; found {len(internal)}."
        )
    if len(external) < MIN_EXTERNAL_LINKS_IN_BODY:
        errors.append(
            f"Need {MIN_EXTERNAL_LINKS_IN_BODY}+ external markdown links in body; found {len(external)}."
        )
    for anchor, _ in internal + external:
        if anchor.strip().lower() in GENERIC_ANCHORS:
            errors.append(f"Generic anchor text not allowed: '{anchor}'.")
    return errors


def validate_policies(body: str, data: dict[str, Any]) -> list[str]:
    errors = []
    lower = body.lower()
    for phrase in POLICY_BANNED_PHRASES:
        if phrase not in lower:
            continue
        if phrase == "keyword stuffing" and re.search(
            r"without keyword stuffing|avoid keyword stuffing|keyword stuffing detected|not keyword stuffing",
            lower,
        ):
            continue
        errors.append(f"Spam-policy risk phrase: '{phrase}'.")
    for phrase in POLICY_RISKY_UNVERIFIED:
        if phrase in lower:
            errors.append(f"Unverifiable claim risk: '{phrase}'.")
    for trig in YMYL_TRIGGERS:
        if trig in lower and "not medical advice" not in lower and "consult a professional" not in lower:
            errors.append(f"YMYL topic '{trig}' requires explicit disclaimer.")
    if data.get("approved") is True and data.get("editorial_reviewed") is not True:
        errors.append("Approved drafts must set editorial_reviewed: true after human review.")
    return errors


def validate_research_metadata(data: dict[str, Any]) -> list[str]:
    errors = []
    for field in ("serp_intent", "funnel_stage", "serp_features", "paa_questions", "serp_analysis"):
        if not data.get(field):
            errors.append(f"Missing research field: {field}.")
    return errors


def validate_full_draft(
    data: dict[str, Any],
    body: str,
    *,
    for_publish: bool,
    humanization_score: int | None = None,
    originality_score: int | None = None,
) -> ComplianceReport:
    report = ComplianceReport()
    recommended = int(data.get("recommended_word_count") or 1200)
    report.metrics["word_count"] = count_words(body)

    report.errors.extend(validate_word_count(body, recommended))
    report.errors.extend(validate_seo(data, body))
    report.errors.extend(validate_aeo_geo(data, body))
    report.errors.extend(validate_aio(body))
    report.errors.extend(validate_sxo(body, data))
    report.errors.extend(validate_user_intent(body, data))
    report.errors.extend(validate_links(body))
    report.errors.extend(validate_policies(body, data))
    report.errors.extend(validate_research_metadata(data))

    read: ReadabilityReport = evaluate_readability(body)
    report.metrics["flesch_ease"] = round(read.flesch_ease, 2)
    report.metrics["fk_grade"] = round(read.fk_grade, 2)
    report.errors.extend(read.issues)

    if for_publish:
        if data.get("approved") is not True:
            report.errors.append("Draft is not approved for publish.")
        if data.get("humanization_verified") is not True:
            report.errors.append("Draft has not passed humanization/compliance verification.")
        if humanization_score is not None and humanization_score < HUMANIZATION_SCORE_MIN:
            report.errors.append(f"Humanization score {humanization_score} below {HUMANIZATION_SCORE_MIN}.")
        if originality_score is not None and originality_score < ORIGINALITY_SCORE_MIN:
            report.errors.append(f"Originality score {originality_score} below {ORIGINALITY_SCORE_MIN}.")

    return report
