"""Shared thresholds for blog content generation and validation."""

from __future__ import annotations

DEFAULT_RECOMMENDED_WORD_COUNT = 1200
WORD_COUNT_BUFFER_ABOVE = 1  # strictly above recommended
WORD_COUNT_MAX_ABOVE = 100  # not more than recommended + this

# Flesch Reading Ease (higher = easier). 60–70 = standard professional web copy.
# Technical SEO vocabulary lowers ease; 50–72 is realistic for expert B2B copy.
FLESCH_EASE_MIN = 50.0
FLESCH_EASE_MAX = 72.0

# Flesch–Kincaid grade level (U.S. school grades).
FK_GRADE_MIN = 7.5
FK_GRADE_MAX = 10.5

# Answer-engine blocks (PAA / FAQ answers embedded in body).
PAA_ANSWER_WORDS_MIN = 45
PAA_ANSWER_WORDS_MAX = 95
SNIPPET_ANSWER_WORDS_MAX = 55

# SEO field lengths
TITLE_LEN_MIN = 35
TITLE_LEN_MAX = 62
META_DESC_LEN_MIN = 120
META_DESC_LEN_MAX = 160

# In-body links (markdown), subtle placement required
MIN_INTERNAL_LINKS_IN_BODY = 4
MIN_EXTERNAL_LINKS_IN_BODY = 3
MIN_H2_SECTIONS = 5
MIN_H3_SECTIONS = 2
MIN_BULLET_LINES = 5

# Humanization gate (kept in sync with readability module)
HUMANIZATION_SCORE_MIN = 80
ORIGINALITY_SCORE_MIN = 62
