# Blog Automation (Approval Gate)

Generates SEO/AEO/GEO/SXO-aligned drafts twice per week. **Nothing publishes without `approved: true` and `editorial_reviewed: true`.**

## Pipeline Stages

1. `trend_collector.py` — RSS trend signals → `automation/blog/data/trends.json`
2. `keyword_planner.py` — SERP intent, funnel stage, PAA questions → `keyword_plan.json`
3. `draft_generator.py` — Markdown drafts (1201–1300 words by default) with in-body links
4. `humanization_gate.py` — Flesch/Kincaid, originality, SEO/AEO/GEO/SXO, policy checks
5. `publish_validator.py` — Final gate; `--publish` only for approved + reviewed drafts

## Content standards (enforced)

| Area | Rule |
|------|------|
| Word count | `recommended_word_count + 1` … `+ 100` (default **1201–1300**) |
| SEO | Title/meta lengths, keyword placement, canonical, H2/H3/bullets |
| AEO/GEO | PAA section, FAQ answers 45–95 words, freshness, schema mentions |
| SXO | SXO checklist, CTA, paragraph length, funnel metadata |
| Readability | Flesch ease 58–72, FK grade 7.5–10.5 |
| Links | ≥4 internal + ≥3 external **in body** (markdown), descriptive anchors |
| Policies | Spam phrases, unverifiable claims, YMYL disclaimer triggers |

## Approval workflow

1. Open `blog/drafts/<slug>.md`
2. Edit for accuracy and brand voice
3. Set `approved: true` and `editorial_reviewed: true`
4. Run `python automation/blog/humanization_gate.py` (must show `verified`)
5. Publish: `python automation/blog/publish_validator.py --publish`  
   Or GitHub Actions → **Publish approved drafts**

## Local run

```bash
python -m pip install -r automation/blog/requirements.txt
python automation/blog/run_pipeline.py
```

Refresh old drafts to new standards:

```bash
python automation/blog/refresh_existing_drafts.py
python automation/blog/humanization_gate.py --notify
```

## Email (optional)

Copy `config.example.json` → `config.local.json` or set GitHub secrets (`BLOG_SMTP_*`).

## Gemini research (free tier — optional)

Copy `gemini_*` fields from `config.example.json` into `config.local.json` (gitignored).

| Setting | Free-tier default | Purpose |
|---------|-------------------|---------|
| `gemini_enabled` | `false` | Must be `true` to allow API |
| `gemini_free_tier` | `true` | Disables Google Search grounding (saves quota) |
| `gemini_max_calls_per_run` | `1` | Max **one** API call per planner run |
| `gemini_max_calls_per_day` | `2` | Max two calls per UTC day |
| `gemini_cache_ttl_days` | `30` | Reuse research without new calls |
| `gemini_cooldown_hours_on_429` | `24` | After quota error, **no API** until cooldown ends |

**Flow:** cache → heuristic research. API only on cache miss, within daily/run caps. On `429`, pipeline uses heuristics only for 24h (no retry spam).

GitHub: secret `GEMINI_API_KEY` + workflow caps (`BLOG_GEMINI_MAX_CALLS=1`, `BLOG_GEMINI_MAX_CALLS_PER_DAY=2`).

**Not a live SERP API** — Gemini infers intent/PAA; free tier quota is very small.
