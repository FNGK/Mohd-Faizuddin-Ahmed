# Self-audit — 2026-10-28T09:11:23

**Verdict:** action_required  |  **Findings:** 3  |  **Checks run:** 10  |  **Skipped:** 0

## Findings (evidence-backed, most severe first)

### 1. [high/CONFIRMED] cadence
No shipped piece logged in 37 days (last 2026-09-21).

- **Evidence:** `{"last_shipped": "2026-09-21", "days_idle": 37, "threshold": 3, "source": "marketing/LOG.md"}`
- **Suggested fix:** Schedule the next queued angle today; investigate why the routine stopped logging.

### 2. [medium/PLAUSIBLE] metrics_fresh
METRICS.md last updated 23 days ago (2026-10-05).

- **Evidence:** `{"last_row": "2026-10-05", "days_stale": 23, "threshold": 8, "source": "marketing/METRICS.md"}`
- **Suggested fix:** Growth Strategist: pull GA4 + Buffer/Meta this week and append a row (never delete rows).

### 3. [low/PLAUSIBLE] voice_watchlist
3 context-dependent word(s) to eyeball (may be legitimate).

- **Evidence:** `{"hits": [{"where": "blog/drafts/aeo-vs-geo-vs-seo-whats-the-difference.md", "line": 133, "word": "unlock", "snippet": "nd GEO are not competitors to SEO; they're what you unlock when your SEO foundation is strong and your p"}, {"where": "blog/drafts/structure-content-for-ai-answer-engines.md", "line": 104, "word": "cheap", "snippet": "and the payoff is unproven for many sites, but it's cheap to add and aligned with where things are headi"}, {"where": "blog/drafts/structure-content-for-ai-answer-engines.md", "line": 157, "word": "cheap", "snippet": "impact is still unproven for many sites, but it is cheap to add and aligned with where AI search is hea"}], "total": 3, "note": "e.g. 'high-leverage' or 'cheap hosting is slow' are fine; only self-positioning uses ('we're affordable') fail."}`
- **Suggested fix:** Judgment layer: read each snippet; rewrite only genuine AI-tells/discount positioning.

