"""Research-style intent enrichment from trends (SERP intent, PAA, funnel stage)."""

from __future__ import annotations

import re
from typing import Any

# People Also Ask patterns derived from SERP research templates per intent cluster.
PAA_BY_CLUSTER: dict[str, list[str]] = {
    "aeo and geo": [
        "What is answer engine optimization in practice?",
        "How do I get cited in AI overviews without keyword stuffing?",
        "Does structured data help generative search visibility?",
        "How long should FAQ answers be for featured snippets?",
        "What is the difference between AEO and traditional SEO?",
        "How do you measure visibility in ChatGPT or Perplexity?",
    ],
    "local growth": [
        "How do I improve Google Business Profile conversions?",
        "Why do map views not turn into phone calls?",
        "What local landing page elements increase bookings?",
        "How often should I update photos and posts on GBP?",
        "Do location pages need unique copy for each city?",
        "How do I track local SEO ROI beyond rankings?",
    ],
    "technical optimization": [
        "What should I fix first in a technical SEO audit?",
        "How does crawl budget affect large ecommerce sites?",
        "When should I use noindex versus canonical consolidation?",
        "What Core Web Vitals matter most for SEO?",
        "How do JavaScript rendering issues hurt indexation?",
        "How do I prioritize schema fixes by revenue impact?",
    ],
    "commercial seo": [
        "How long does recovery take after a Google core update?",
        "Should I rewrite all pages after a traffic drop?",
        "How do I separate a penalty from a core update?",
        "What E-E-A-T signals matter most for YMYL niches?",
        "How do I fix keyword cannibalization quickly?",
        "What should leadership see in an SEO recovery report?",
    ],
}

SERP_FEATURE_KEYWORDS = {
    "featured_snippet": ("how", "what", "why", "when", "best", "vs"),
    "local_pack": ("near me", "local", "map", "city", "area"),
    "video": ("video", "tutorial", "watch"),
    "discussion": ("reddit", "forum", "opinion"),
}


def infer_serp_intent(term: str, cluster: str) -> str:
    t = term.lower()
    if any(w in t for w in ("buy", "pricing", "hire", "agency", "consultant", "cost")):
        return "commercial"
    if any(w in t for w in ("how to", "guide", "checklist", "steps", "template")):
        return "informational"
    if any(w in t for w in ("vs", "compare", "alternative", "best")):
        return "comparison"
    if cluster == "local growth":
        return "local_commercial"
    if cluster == "technical optimization":
        return "informational_technical"
    return "informational"


def infer_funnel_stage(serp_intent: str, cluster: str) -> str:
    if serp_intent in ("commercial", "local_commercial"):
        return "decision"
    if serp_intent == "comparison":
        return "consideration"
    if cluster == "commercial seo" and "recovery" in serp_intent:
        return "consideration"
    return "awareness" if serp_intent.startswith("informational") else "consideration"


def infer_serp_features(term: str, trend_titles: list[str]) -> list[str]:
    features: list[str] = []
    blob = f"{term} {' '.join(trend_titles[:8])}".lower()
    for feature, triggers in SERP_FEATURE_KEYWORDS.items():
        if any(tr in blob for tr in triggers):
            features.append(feature)
    if not features:
        features.append("organic_blue_link")
    return features


def build_paa_questions(term: str, cluster: str, count: int = 5) -> list[str]:
    base = list(PAA_BY_CLUSTER.get(cluster, PAA_BY_CLUSTER["commercial seo"]))
    # Previously stripped everything from " seo" onward (leftover from the old
    # "<term> seo strategy" keyword-suffix pattern keyword_planner no longer
    # generates—see its build_keywords() docstring). That regex now mangles
    # legitimate terms that contain "seo" mid-phrase, e.g. "technical seo audit"
    # -> "technical", producing "How does technical affect organic revenue in
    # 2026?" instead of a real question. Use the term as written.
    term_clean = term.strip()
    tailored = [f"How does {term_clean} affect organic revenue in 2026?"] + base
    seen: set[str] = set()
    out: list[str] = []
    for q in tailored:
        key = q.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(q)
        if len(out) >= count:
            break
    return out


def serp_analysis_summary(
    term: str,
    serp_intent: str,
    funnel_stage: str,
    features: list[str],
    trend_titles: list[str],
) -> str:
    competitors = "; ".join(trend_titles[:3]) if trend_titles else "industry publishers"
    feature_txt = ", ".join(features)
    return (
        f"SERP snapshot for '{term}': dominant intent is **{serp_intent}** at the **{funnel_stage}** "
        f"funnel stage. Observed SERP features include {feature_txt}. "
        f"Recent titles in the news layer include {competitors}. "
        "This draft targets extractable answers, corroboration, and conversion clarity (SXO)."
    )


def enrich_idea(idea: dict[str, Any], term: str, trend_titles: list[str] | None = None) -> dict[str, Any]:
    cluster = str(idea.get("intent_cluster", "commercial seo"))
    titles = trend_titles or []
    serp_intent = infer_serp_intent(term, cluster)
    funnel_stage = infer_funnel_stage(serp_intent, cluster)
    features = infer_serp_features(term, titles)
    paa = build_paa_questions(term, cluster)
    enriched = dict(idea)
    enriched["serp_intent"] = serp_intent
    enriched["funnel_stage"] = funnel_stage
    enriched["serp_features"] = features
    enriched["paa_questions"] = paa
    enriched["serp_analysis"] = serp_analysis_summary(term, serp_intent, funnel_stage, features, titles)
    if "recommended_word_count" not in enriched:
        enriched["recommended_word_count"] = 1200
    enriched.setdefault("research_source", "heuristic")
    enriched.setdefault("gemini_enriched", False)
    return enriched
