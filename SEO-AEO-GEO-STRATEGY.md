# SEO With Faiz — AEO/GEO Wedge Strategy & 90-Day Roadmap

_Prepared 2026-06-25. Wedge decision: **Answer Engine Optimization / Generative Engine Optimization (AI search visibility)**._

## 1. Reality baseline (live Ahrefs data)

| Metric | Value | Source |
|---|---|---|
| Domain Rating | **0** | Ahrefs `public-domain-rating-free`, 2026-06-25 |

> Keyword/competitor volume endpoints were **not available on the connected Ahrefs plan** ("Insufficient plan" — Keywords Explorer / Site Explorer need the API add-on). Volume & difficulty below are **expert estimates**, banded, not live numbers. Upgrade the API plan (or export from the Ahrefs web UI) to replace these with exact figures.

**Strategic consequence of DR 0:** head terms — `seo services`, `seo agency`, `seo consultant`, `best seo company` — are owned by DR 80–91 sites (Ahrefs, Semrush, WebFX, Neil Patel) with thousands of referring domains. **They are unwinnable in the near term.** Effort spent there returns ~0. We win by owning a low-competition, high-intent, emerging category and expanding outward.

## 2. Why the AEO/GEO wedge

- **Low competition, high growth.** "Answer engine optimization" / "generative engine optimization" SERPs are young; authority requirements are far lower than classic SEO terms.
- **You're already built for it.** Existing schema graph, FAQ/HowTo/Speakable markup, and answer-first blocks are exactly what AEO rewards.
- **Defensible positioning.** "The AI-search visibility specialist" is a sharper, more memorable claim than "an SEO consultant."
- **Compounding.** Getting cited in AI answers *and* ranking organically reinforce each other.

## 3. Keyword map (3 tiers by winnability)

Difficulty/volume = estimated bands (Low/Med/High). Target = page that should own the term.

### Tier 1 — Win now (DR 0-friendly: long-tail, question, local)
| Keyword | Intent | Est. KD | Target page |
|---|---|---|---|
| how to rank in ai overviews | Informational | Low | Blog spoke |
| how to get cited by chatgpt | Informational | Low | Blog spoke |
| what is answer engine optimization | Informational | Low | AEO pillar |
| generative engine optimization vs seo | Informational | Low | Blog spoke |
| schema markup for ai search | Informational | Low | Blog spoke |
| seo consultant hyderabad / seo services india | Commercial/Local | Low-Med | India/location page |
| technical seo audit checklist | Informational | Low-Med | Audit resource → audit service |

### Tier 2 — Win in 3–6 months (after initial authority + content depth)
| Keyword | Intent | Est. KD | Target page |
|---|---|---|---|
| answer engine optimization services | Commercial | Med | **AEO service money page** |
| generative engine optimization services | Commercial | Med | AEO/GEO service page |
| ai search optimization | Commercial/Info | Med | AEO service page |
| international seo consultant | Commercial | Med | International SEO service page |
| saas seo consultant / b2b seo | Commercial | Med | Vertical page |
| technical seo audit service | Commercial | Med | **SEO audit money page ($100 wedge)** |
| affordable seo consultant | Commercial | Med | Pricing / home |

### Tier 3 — Aspirational (only after DR climbs + topical authority)
`answer engine optimization` · `ai seo` · `generative engine optimization` · `seo services usa` · `seo consultant`

## 4. Content & page gaps to close (priority order)

1. **`/services/answer-engine-optimization.html`** — the wedge money page. Does not exist; this is the #1 build.
2. **`/services/seo-audit.html`** — dedicated page for the $100 audit (your conversion wedge), targeting `seo audit service` / `website seo audit`.
3. **AEO pillar + cluster** — "What is Answer Engine Optimization" pillar linking 6–10 spokes (now auto-seeded by the fixed pipeline).
4. **`/seo-services-india.html`** (and later US/UK/AU market pages) — geo-intent currently has nowhere to land.
5. **Vertical page(s)** — `saas-seo` / `b2b-seo`, higher commercial intent than head terms.
6. **`how much does seo cost` + comparison pages** — BOFU, matches the "affordable, direct-with-Faiz" angle.

## 5. Authority plan (DR 0 → traction)

Content alone won't rank at DR 0. In parallel:
- Run the existing `outreach/` + `automation/outreach/deploy_backlink_strategy.py` wave for relevant, real links.
- Digital PR / guest posts on SEO + marketing blogs as "the AI-search visibility specialist."
- Get cited where LLMs source answers (Reddit, LinkedIn, industry roundups, Quora) — this doubles as GEO.
- Podcasts / HARO-style expert quotes; feed the `mentions.html` proof loop.

## 6. 90-day roadmap

- **Weeks 1–2:** Build AEO/GEO service page + SEO audit page. Re-optimize home/services titles toward the wedge. Tighten internal links into the new money pages.
- **Weeks 3–6:** Ship the AEO pillar + 6–8 spokes (pipeline now produces unique, real-keyword drafts). Publish India/location page + `how much does seo cost`.
- **Weeks 7–10:** Authority sprint — 10–15 quality links, 2–3 guest posts, AI-source placements. Add vertical (SaaS) page.
- **Weeks 11–12:** Measure AI-Overview impressions + audit bookings; double down on what moves; expand to international/US market pages.

## 7. KPIs (pipeline-first, not vanity)

- **AI-surface citations / AI Overview impressions** (the wedge metric) — GSC + manual AI-answer checks.
- **$100 audit bookings** as the leading conversion signal.
- **DR & referring domains** trend (from 0).
- **Non-brand impressions/clicks** on AEO + audit + India terms.

## 8. Automation fix shipped (this session)

`automation/blog/keyword_planner.py` + `intent_content.py`:
- Removed the `"<term> seo strategy"` suffix bug that generated zero-volume keywords.
- Seeds re-pointed to real AEO/GEO + commercial queries; secondary keywords now grammatical long-tails.
- Fixed hardcoded per-cluster titles (was collapsing 15 seeds → 4 clone posts) → unique, acronym-correct titles per keyword.
- ChatGPT/GEO/overview terms now route into the AEO cluster.

**Known follow-up (not in this session's scope):** article _bodies_ are still cluster-templated (4 base templates in `intent_content.py`), so distinct titles can share body structure. Recommend moving body generation to per-keyword outlines next.
