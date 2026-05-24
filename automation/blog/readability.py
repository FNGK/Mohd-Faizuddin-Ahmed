"""Flesch–Kincaid and answer-length readability metrics."""

from __future__ import annotations

import re
from dataclasses import dataclass

from content_config import (
    FLESCH_EASE_MAX,
    FLESCH_EASE_MIN,
    FK_GRADE_MAX,
    FK_GRADE_MIN,
    PAA_ANSWER_WORDS_MAX,
    PAA_ANSWER_WORDS_MIN,
    SNIPPET_ANSWER_WORDS_MAX,
)

WORD_RE = re.compile(r"\b[\w']+\b")
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
SYLLABLE_RE = re.compile(r"[aeiouy]+", re.IGNORECASE)


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def count_sentences(text: str) -> int:
    parts = [p.strip() for p in SENTENCE_SPLIT.split(text.strip()) if p.strip()]
    return max(1, len(parts))


def estimate_syllables(word: str) -> int:
    w = re.sub(r"[^a-zA-Z]", "", word).lower()
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    groups = SYLLABLE_RE.findall(w)
    count = len(groups)
    if w.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def count_syllables(text: str) -> int:
    return sum(estimate_syllables(w) for w in WORD_RE.findall(text))


def flesch_reading_ease(text: str) -> float:
    words = count_words(text)
    if words == 0:
        return 0.0
    sentences = count_sentences(text)
    syllables = count_syllables(text)
    return 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)


def flesch_kincaid_grade(text: str) -> float:
    words = count_words(text)
    if words == 0:
        return 0.0
    sentences = count_sentences(text)
    syllables = count_syllables(text)
    return 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59


@dataclass
class ReadabilityReport:
    flesch_ease: float
    fk_grade: float
    issues: list[str]

    def passed(self) -> bool:
        return not self.issues


def evaluate_readability(body: str, faq_section: str | None = None) -> ReadabilityReport:
    issues: list[str] = []
    ease = flesch_reading_ease(body)
    grade = flesch_kincaid_grade(body)

    if ease < FLESCH_EASE_MIN or ease > FLESCH_EASE_MAX:
        issues.append(
            f"Flesch Reading Ease {ease:.1f} outside target band {FLESCH_EASE_MIN}–{FLESCH_EASE_MAX}."
        )
    if grade < FK_GRADE_MIN or grade > FK_GRADE_MAX:
        issues.append(
            f"Flesch–Kincaid grade {grade:.1f} outside target band {FK_GRADE_MIN}–{FK_GRADE_MAX}."
        )

    # Featured-snippet style opening (first sentence of first non-heading paragraph)
    for block in body.split("\n\n"):
        block = block.strip()
        if not block or block.startswith("#"):
            continue
        first_sentence = SENTENCE_SPLIT.split(block)[0]
        fp_words = count_words(first_sentence)
        if fp_words > SNIPPET_ANSWER_WORDS_MAX:
            issues.append(
                f"Opening answer sentence is {fp_words} words; keep under {SNIPPET_ANSWER_WORDS_MAX} for snippet/AEO targets."
            )
        break

    faq_text = faq_section or ""
    if "### " in body or "## People also ask" in body or "## Frequently asked questions" in body:
        faq_text = body
    for match in re.finditer(r"^###\s+(.+)$\n+([^#]+)", faq_text, flags=re.MULTILINE):
        answer = match.group(2).strip()
        aw = count_words(answer)
        if aw < PAA_ANSWER_WORDS_MIN or aw > PAA_ANSWER_WORDS_MAX:
            issues.append(
                f"FAQ answer '{match.group(1)[:40]}…' is {aw} words; need {PAA_ANSWER_WORDS_MIN}–{PAA_ANSWER_WORDS_MAX}."
            )

    return ReadabilityReport(flesch_ease=ease, fk_grade=grade, issues=issues)
