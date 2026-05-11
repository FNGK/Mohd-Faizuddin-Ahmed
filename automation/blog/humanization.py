"""Heuristic humanization and originality checks for blog drafts."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

AI_CLICHES = (
    "in today's digital landscape",
    "in conclusion",
    "it's important to note",
    "delve into",
    "leverage",
    "robust",
    "seamlessly",
    "game-changer",
    "unlock the power",
    "at the end of the day",
    "comprehensive guide",
    "navigate the ever-changing",
    "cutting-edge",
    "holistic approach",
    "synergy",
    "paradigm",
)

TEMPLATE_PHRASES = (
    "what teams should do in 2026",
    "this article explains",
    "readers should leave with",
    "practical next steps",
    "teams should leave with",
)

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
WORD_RE = re.compile(r"[a-z0-9']+")
SHINGLE_RE = re.compile(r"[a-z0-9']+")


@dataclass
class HumanizationReport:
    score: int
    originality_score: int
    verified: bool
    issues: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)

    def to_frontmatter(self) -> dict[str, object]:
        return {
            "humanization_score": self.score,
            "originality_score": self.originality_score,
            "humanization_verified": self.verified,
            "humanization_issues": self.issues[:12],
            "humanization_metrics": {k: round(v, 3) for k, v in self.metrics.items()},
        }


def _sentences(text: str) -> list[str]:
    parts = [s.strip() for s in SENTENCE_SPLIT.split(text.strip()) if s.strip()]
    return parts or [text.strip()]


def _words(text: str) -> list[str]:
    return WORD_RE.findall(text.lower())


def _shingles(text: str, size: int = 5) -> set[tuple[str, ...]]:
    tokens = SHINGLE_RE.findall(text.lower())
    if len(tokens) < size:
        return set()
    return {tuple(tokens[i : i + size]) for i in range(len(tokens) - size + 1)}


def _jaccard(a: set[tuple[str, ...]], b: set[tuple[str, ...]]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def collect_reference_corpus(repo_root: Path, exclude_path: Path | None = None) -> list[str]:
    corpus: list[str] = []
    drafts_dir = repo_root / "blog" / "drafts"
    posts_dir = repo_root / "blog" / "posts"
    for folder in (drafts_dir, posts_dir):
        if not folder.is_dir():
            continue
        for path in folder.glob("*"):
            if path.suffix not in {".md", ".html"}:
                continue
            if exclude_path and path.resolve() == exclude_path.resolve():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if path.suffix == ".html":
                text = re.sub(r"<[^>]+>", " ", text)
            try:
                if path.suffix == ".md" and text.startswith("---"):
                    _, body = text.split("\n---\n", 1)
                    corpus.append(body)
                else:
                    corpus.append(text)
            except ValueError:
                corpus.append(text)
    return corpus


def originality_against_corpus(body: str, corpus: list[str]) -> tuple[int, float]:
    body_shingles = _shingles(body)
    if not body_shingles:
        return 0, 1.0
    max_overlap = 0.0
    for other in corpus:
        overlap = _jaccard(body_shingles, _shingles(other))
        max_overlap = max(max_overlap, overlap)
    score = int(max(0, min(100, round((1.0 - max_overlap) * 100))))
    return score, max_overlap


def score_humanization(body: str, primary_keyword: str = "") -> HumanizationReport:
    issues: list[str] = []
    metrics: dict[str, float] = {}
    lower = body.lower()
    sentences = _sentences(body)
    words = _words(body)
    word_count = len(words)
    metrics["word_count"] = float(word_count)

    if word_count < 520:
        issues.append(f"Body is short for a solution post ({word_count} words; aim for 520+).")

    lengths = [len(s.split()) for s in sentences]
    if lengths:
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
        metrics["sentence_length_variance"] = variance
        if variance < 18:
            issues.append("Sentence rhythm is flat; mix short and longer sentences.")

    unique_ratio = len(set(words)) / word_count if word_count else 0.0
    metrics["lexical_diversity"] = unique_ratio
    if unique_ratio < 0.42:
        issues.append("Vocabulary repeats too often for a natural read.")

    contractions = len(re.findall(r"\b(?:you're|we're|it's|don't|can't|won't|isn't|aren't|i've|i'm)\b", lower))
    metrics["contractions"] = float(contractions)
    if contractions < 2:
        issues.append("Add a few contractions so the voice sounds spoken, not generated.")

    questions = sum(1 for s in sentences if "?" in s)
    metrics["question_sentences"] = float(questions)
    if questions < 1:
        issues.append("Include at least one direct question that mirrors reader intent.")

    second_person = len(re.findall(r"\byou\b|\byour\b", lower))
    metrics["second_person_hits"] = float(second_person)
    if second_person < 8:
        issues.append("Address the reader directly more often with you/your.")

    if primary_keyword:
        keyword_hits = lower.count(primary_keyword.lower())
        metrics["primary_keyword_hits"] = float(keyword_hits)
        if keyword_hits < 1:
            issues.append("Primary keyword is missing from the body.")
        if keyword_hits > 6:
            issues.append("Primary keyword is stuffed; keep it natural.")

    cliche_hits = sum(1 for phrase in AI_CLICHES if phrase in lower)
    metrics["ai_cliche_hits"] = float(cliche_hits)
    if cliche_hits:
        issues.append("Trim generic AI phrasing and replace with concrete examples.")

    template_hits = sum(1 for phrase in TEMPLATE_PHRASES if phrase in lower)
    metrics["template_hits"] = float(template_hits)
    if template_hits >= 2:
        issues.append("Template boilerplate is still visible; rewrite intros and closings.")

    passive = len(
        re.findall(
            r"\b(?:is|are|was|were|been|being)\s+\w+ed\b",
            lower,
        )
    )
    metrics["passive_hits"] = float(passive)
    if passive > 12:
        issues.append("Too much passive voice; lead with who does what.")

    score = 100
    score -= min(35, len(issues) * 7)
    score -= min(20, cliche_hits * 8)
    score -= min(15, template_hits * 6)
    if word_count < 520:
        score -= 12
    if unique_ratio < 0.42:
        score -= 8
    score = max(0, min(100, score))

    return HumanizationReport(
        score=score,
        originality_score=0,
        verified=False,
        issues=issues,
        metrics=metrics,
    )


def evaluate_draft(
    body: str,
    primary_keyword: str,
    repo_root: Path,
    draft_path: Path | None = None,
    *,
    min_score: int = 72,
    min_originality: int = 62,
) -> HumanizationReport:
    report = score_humanization(body, primary_keyword)
    corpus = collect_reference_corpus(repo_root, exclude_path=draft_path)
    originality, overlap = originality_against_corpus(body, corpus)
    report.originality_score = originality
    report.metrics["max_shingle_overlap"] = overlap
    if originality < min_originality:
        report.issues.append(
            f"Too much overlap with other site copy (originality {originality}; need {min_originality}+)."
        )
    if report.score < min_score:
        report.issues.append(f"Humanization score {report.score} is below the {min_score} threshold.")
    report.verified = report.score >= min_score and originality >= min_originality and not any(
        issue.startswith("Body is short") for issue in report.issues
    )
    return report
