# Self-audit — 2026-10-12T12:23:05

**Verdict:** action_required  |  **Findings:** 2  |  **Checks run:** 9  |  **Skipped:** 0

## Findings (evidence-backed, most severe first)

### 1. [high/CONFIRMED] cadence
No shipped piece logged in 21 days (last 2026-09-21).

- **Evidence:** `{"last_shipped": "2026-09-21", "days_idle": 21, "threshold": 3, "source": "marketing/LOG.md"}`
- **Suggested fix:** Schedule the next queued angle today; investigate why the routine stopped logging.

### 2. [low/PLAUSIBLE] voice_watchlist
3 context-dependent word(s) to eyeball (may be legitimate).

- **Evidence:** `{"hits": [{"where": "blog/drafts/aeo-vs-geo-vs-seo-whats-the-difference.md", "line": 131, "word": "unlock", "snippet": "nd GEO are not competitors to SEO; they're what you unlock when your SEO foundation is strong and your p"}, {"where": "blog/drafts/structure-content-for-ai-answer-engines.md", "line": 102, "word": "cheap", "snippet": "and the payoff is unproven for many sites, but it's cheap to add and aligned with where things are headi"}, {"where": "blog/drafts/structure-content-for-ai-answer-engines.md", "line": 155, "word": "cheap", "snippet": "impact is still unproven for many sites, but it is cheap to add and aligned with where AI search is hea"}], "total": 3, "note": "e.g. 'high-leverage' or 'cheap hosting is slow' are fine; only self-positioning uses ('we're affordable') fail."}`
- **Suggested fix:** Judgment layer: read each snippet; rewrite only genuine AI-tells/discount positioning.

