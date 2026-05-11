"""Intent-specific, solution-led article bodies for blog drafts."""

from __future__ import annotations

from typing import Any


def human_title(term: str, intent_cluster: str) -> str:
    term_clean = term.strip().title()
    if intent_cluster == "local growth":
        return f"Local SEO That Turns Map Views Into Booked Jobs in 2026"
    if intent_cluster == "technical optimization":
        return f"Technical SEO Priorities When Crawl Budget and Revenue Both Matter"
    if intent_cluster == "aeo and geo":
        return f"AI Search Visibility: What to Fix Before You Chase New Formats"
    if intent_cluster == "commercial seo":
        return f"Recovering After a Google Core Update Without Burning the Site Down"
    return f"{term_clean}: A Practical Playbook for 2026"


def build_body(idea: dict[str, Any]) -> str:
    cluster = (idea.get("intent_cluster") or "").strip().lower()
    builders = {
        "local growth": _body_local_growth,
        "technical optimization": _body_technical,
        "aeo and geo": _body_aeo_geo,
        "commercial seo": _body_core_update,
    }
    builder = builders.get(cluster, _body_generic)
    return builder(idea)


def _body_local_growth(idea: dict[str, Any]) -> str:
    kw = idea.get("primary_keyword") or "local seo conversion strategy"
    city = idea.get("geo_hint") or "your service area"
    return f"""## Why map rankings stall even when reviews look fine

If you run a location-based business, you have probably seen the pattern: impressions climb on Google Maps, calls trickle in, and the CRM still shows empty slots on Tuesday afternoon. That gap is rarely a "more content" problem. It is usually a **local SEO conversion strategy** issue—searchers find you, but the path from profile to booked job has friction you cannot see in a ranking report.

Start by treating the Business Profile as a landing page, not a directory listing. Photos should answer the first three objections your front desk hears every week. Services need plain-language names that match how people type, not internal SKU labels. If you serve {city}, say where you go and where you do not; vague service areas train the wrong clicks.

## Fix the profile-to-phone leak first

Pull thirty days of GBP insights and compare **calls, direction requests, and website taps** against actual leads. When website taps outperform calls, your site is probably asking for trust you have not earned on mobile yet. When calls lag but impressions are high, your hours, categories, or review themes may be sending mixed signals.

On the site, every location page should open with the job you solve, the response window, and proof from that market. One CTA above the fold—call, book, or short form—beats three equal buttons. Match NAP in footer, schema, and the profile exactly; I have seen rankings hold while conversions died because a tracking number swapped the display phone without updating structured data.

## On-page and internal links that support bookings

Use intent-based keywords in headings only where they mirror a real query. A heading like "emergency plumber in {city}" works when the page actually documents emergency coverage and pricing expectations. Stuffing city names into every H2 reads robotic and hurts both trust and AI summaries.

Internally, link from high-trust pages—about, case studies, resources—to the locations that need velocity. Anchor text should describe the outcome ("same-day HVAC in {city}") rather than repeating the same {kw} phrase. Add FAQ blocks that answer scheduling, insurance, and "do you serve my neighborhood" in complete sentences; those strings feed AI overviews and voice results without a separate gimmick layer.

## Measurement that proves local SEO is working

Track **qualified actions**, not vanity ranks. A simple sheet works: profile views, calls over sixty seconds, form starts, and booked jobs tagged with source. Compare week over week and against seasonal baselines. If rankings rise but booked jobs flatline, audit the post-click experience before you publish another blog post.

When you report upward, tie actions to revenue. Leadership funds fixes faster when you show that trimming a clunky multi-step form recovered eleven percent of mobile leads—not when you show a green arrow on a keyword tracker.

## Quick wins for this week

- Align GBP categories and hours with what sales promises on calls.
- Put one proof block above the fold on your busiest location page.
- Route internal links from case studies to the cities that need bookings.

## A sane 30-day sequence

Week one: profile, NAP, and call tracking alignment. Week two: rewrite top location pages for clarity and proof. Week three: internal links and FAQ/schema cleanup. Week four: review response themes and photo refresh based on what prospects asked on sales calls. That cadence keeps your **local seo conversion strategy** tied to operations, not a quarterly deck.

You do not need a perfect stack on day one. You need a visible path from search to booked work—and the discipline to fix the step where people actually drop off."""


def _body_technical(idea: dict[str, Any]) -> str:
    kw = idea.get("primary_keyword") or "technical seo prioritization"
    return f"""## Crawl budget is a business constraint, not a specialist hobby

Technical SEO prioritization gets fuzzy when every audit ships fifty red rows. The question that matters for revenue is simpler: **which fixes change how Google stores and serves your money pages this month?** If you cannot connect a ticket to crawl, indexation, or render quality on URLs that convert, it waits.

Begin with a segmented crawl export. Group templates: product, category, content, faceted paths, and legacy parameters. Sort by internal links in, organic sessions, and conversion rate. The overlap list is your short stack—not the longest list of hreflang warnings on pages with zero demand.

## Indexation and duplication before cosmetics

Check **coverage and canonical behavior** on templates that moved in the last two site releases. Soft 404s, accidental noindex on paginated series, and parameter duplicates often arrive from a plugin or CMS default—not malice. Fix those before you debate image lazy-load strategy.

For large catalogs, faceted navigation is where crawl budget bleeds. Decide which parameter combinations deserve an indexable URL and which should consolidate. Marketing will want long-tail doors; engineering will want fewer paths. Document the rule set and enforce it in the CMS so new filters do not reopen the hole next quarter.

## Core Web Vitals as a ranking tie-breaker, not a religion

Measure CWV on templates with traffic, not on the homepage alone. A product template with thin margins and heavy scripts hurts more than a slow careers page. Prioritize **LCP on top landing URLs** and INP on flows with multi-step forms. Send developers one template and one filmstrip; repeating site-wide scores without a URL list wastes everyone's week.

When Vite or tag managers balloon main-thread work, negotiate what must run before first interaction. Often you can defer non-essential pixels on organic landing pages without touching the global stack.

## Structured data that matches what is on the page

Schema is not seasoning. Add types only where the visible copy supports them. Product, FAQ, and breadcrumb markup should mirror what a human sees; mismatches invite rich-result loss and make AI summaries harder to trust. Validate after deploy, not only in staging—production templates love to drift.

If you are weighing **{kw}** against content projects, use this filter: schema and canonical fixes on high-intent URLs usually beat net-new articles when indexation is leaky. Articles help when the URLs they support already render cleanly.

## Quick wins for this week

- Export crawl stats for templates with revenue tied to them.
- Fix unintended noindex or canonical drift on one high-traffic template.
- Defer non-essential scripts on a single money URL and remeasure INP.

## Release discipline and monitoring

Ship technical changes in small batches with before/after log samples from Search Console and server logs. Watch crawl stats, indexed page counts on key templates, and organic sessions with a two-week lag—not forty-eight hours of panic.

Run a monthly **technical SEO prioritization** review with product and engineering: top five URLs by revenue at risk, top five fixes shipped, top five deferred with reasons. That rhythm keeps the backlog honest and stops the team from chasing lighthouse scores on pages nobody finds.

Technical work earns trust when stakeholders see fewer duplicate URLs in coverage, faster renders on checkout paths, and steadier impressions on category templates you actually want to rank. Everything else is backlog until it touches those outcomes."""


def _body_aeo_geo(idea: dict[str, Any]) -> str:
    kw = idea.get("primary_keyword") or "ai search visibility"
    return f"""## AI answers reward clarity, not another "AI SEO" landing page

Teams hear "AI search" and spin up a new hub with vague claims. Searchers and answer engines reward something quieter: **pages that resolve one intent completely**, with language models can quote without guessing. Your **ai search visibility** plan should start with the questions sales and support already answer ten times a week.

List those questions verbatim from tickets, call notes, and chat logs. Map each to a URL that exists—or should exist—as a single, authoritative answer. If two pages compete, merge or differentiate sharply. AI summaries hate polite duplication as much as classic blue-link results do.

## Make answers extractable without dumbing down the brand

Lead sections with a direct response in plain English, then deepen with steps, constraints, and examples. Use headings that track real queries ("how long does X take," "what voids a warranty") instead of metaphor-heavy titles. Short lists help when items are truly parallel; avoid bullet farms that repeat the same sentence shape.

Add named entities you are allowed to mention—products, standards, regions—and define them once. Answer engines stitch facts more reliably when proper nouns are consistent across service pages, docs, and posts. Keep opinions labeled as guidance; mark procedures as steps with prerequisites.

## GEO is geography plus corroboration

For **generative engine optimization**, local proof still matters. Link location pages to verifiable signals: licenses, associations, and third-party reviews you do not control. When AI systems summarize local providers, they lean on corroboration across the open web. A thin GBP and a website that never names the city will lose to a competitor with messy design but consistent citations.

Refresh "last updated" when facts change—pricing bands, regulations, product lines. Stale dates do not kill rankings overnight, but they reduce trust in snippets and AI cards where freshness is implied.

## Technical hygiene that helps machines quote you

Fast, render-stable pages still win. Ensure critical copy is in HTML, not hidden behind delayed tabs or empty shells. FAQ schema only where the text is visible. Robots and canonical tags should not fence off the very URLs you want quoted.

Internally, link from high-citation posts on your site to the URLs you want treated as canonical answers. Use descriptive anchors; avoid "click here." External PR and partner pages help when they repeat the same facts in independent voices—without copy-paste press releases.

## How to measure progress without fake AEO scores

Track branded and non-branded **impressions in Search Console**, referral patterns from answer-heavy surfaces where available, and assisted conversions on pages you marked as answer hubs. Qualitative checks matter too: run the top ten buyer questions through major AI interfaces monthly and note which URLs get cited—or get skipped.

If citations go to competitors with thinner pages, compare structure: do they state a number, a timeline, or a constraint in the first paragraph? Imitate the clarity, not the fluff.

## Quick fixes you can ship this week

- Merge duplicate FAQ answers into one canonical URL.
- Add a dated "last reviewed" line on pricing or policy pages.
- Link proof assets from the first screen of each answer hub.

## A practical ninety-day rollout

Month one: question inventory and dedupe. Month two: rewrite priority URLs with extractable intros and proof. Month three: internal links, schema cleanup, and a review cadence with sales to capture new objections. That is a grounded **ai search visibility** program—fewer buzzwords, more sentences a tired buyer can skim at midnight and still understand."""


def _body_core_update(idea: dict[str, Any]) -> str:
    kw = idea.get("primary_keyword") or "google core update recovery"
    return f"""## After a core update, panic edits usually make things worse

When traffic drops after a Google core update, the first instinct is to rewrite everything. That often swaps a clear problem for a muddy one. **Google core update recovery** starts with separating signal loss on templates you care about from noise on pages that never sold.

If you are staring at a week-over-week cliff, ask which URLs actually feed revenue—not which keywords merely look embarrassing in a rank tracker. Which templates would you miss if they disappeared tomorrow?

Export Search Console for the hit window: impressions, clicks, and average position by page and query. Tag URLs by template and intent. If entire categories slid together, suspect quality or duplication patterns—not a single bad paragraph.

## Diagnose before you "fix" content

Compare winners and losers on the same site. Winners with thin copy suggest the issue was not word count. Losers with heavy boilerplate suggest consolidation or sharper differentiation. Look for **cannibalization**: two URLs chasing the same intent with interchangeable intros. Merge or refocus them before you add new posts.

Check technical regressions that coincided with the update window: accidental noindex, redirect chains after a CMS push, or faceted URLs that bloomed unchecked. Updates amplify existing weaknesses; they rarely invent a penalty from a clean baseline.

## Recovery moves that hold up under scrutiny

Improve **first-hand experience** on money pages: original photos, named processes, timelines, and limits. Replace generic "we are passionate about" sections with specifics a competitor cannot paste. Update author and editorial notes where E-E-A-T matters for your niche.

Prune or noindex low-value doors that dilute the site: tag spam, near-duplicate location pages, and legacy campaigns. A smaller, clearer index often rebounds faster than another content surge.

For queries you still need to win, strengthen internal links from surviving authoritative pages. Anchor with intent language, not exact-match repetition. Pair on-page work with outreach only where it earns real citations—not syndicated fluff.

## Quick wins for this week

- Tag winners and losers in Search Console before you edit copy.
- Merge one pair of cannibalizing URLs and redirect the weaker page.
- Add a visible "last updated" note on a policy or pricing page.

## Pace and communication

Ship changes in waves every two to three weeks so you can read lagged data. Document hypotheses: "merged A and B," "added pricing table," "removed faceted indexation." Leadership wants a timeline; give them milestones tied to coverage and qualified traffic, not daily rank checks.

If you run paid or email alongside organic, don't attribute blended swings solely to the update. Hold channel reports side by side so **{kw}** efforts don't chase the wrong lever.

## When to call the work "recovered"

Recovery is not only returning to a traffic peak. It is **stable impressions on priority URLs**, improved click-through on rewritten titles, and form or revenue metrics that match or beat the pre-drop baseline on a seasonally adjusted view. If rankings return but conversions stay flat, you still have a landing-page problem—just not an update-shaped one.

Used with patience, this sequence respects how core updates work: they re-score the index you already built. Clean the index, clarify the pages that matter, and prove experience where buyers decide—not in a frantic weekend of synonym swaps.

Keep a short changelog per URL so the next update is a comparison, not a guessing game."""


def _body_generic(idea: dict[str, Any]) -> str:
    term = idea.get("primary_keyword") or idea.get("term") or "seo strategy"
    return f"""## Start with the job the reader is trying to finish

Most {term} advice fails because it describes tactics without naming the outcome. Before you add another tool, write the single sentence a stakeholder agrees on: what should improve, for whom, and by when. That sentence keeps the work honest when rankings flicker.

## Build a short list of pages that matter

Export organic landing URLs with sessions and conversions. Mark the top ten that feed pipeline. Those URLs get the first fixes—copy, internal links, schema, and speed—not the long tail of old campaigns.

## Match the message to the query

Headings should sound like questions buyers ask. Answer in the first lines, then show steps, limits, and proof. If you cannot point to a case, use operational detail only your team would know.

## Review monthly, ship in small batches

Change a handful of URLs at a time and note what moved in Search Console and in leads. **{term}** work compounds when you keep a log, not when you chase every industry tweet.

## What to do this week

Pick one money page, one technical blocker, and one internal link gap. Ship those before you plan the next quarter. Readers land on your site to solve a problem—give them the next step they can take today."""
