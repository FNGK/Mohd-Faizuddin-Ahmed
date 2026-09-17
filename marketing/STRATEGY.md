# SEO With Faiz — Growth Strategy (living document)

> Owned by the Growth Strategist role. Reviewed and updated every Monday.
> All roles read this before producing anything. The full operating manual
> and Elite Audit Protocol live in the `swf-marketing-team` skill.

## Current objective (Q3 2026)

Build enough visible, verifiable authority that enterprise and growth-stage
buyers researching "who should rebuild/grow our site" find Faiz, believe
Faiz, and book a strategy call. Organic only — no paid spend.

North-star signals (in order): strategy-call inquiries → site sessions from
social/search → branded searches → follower quality (not count).

## Positioning (do not drift)

One senior partner who designs, builds, and grows revenue-critical websites —
custom/3D/WordPress/Shopify Plus/Wix/Magento + technical/international SEO +
performance marketing. Founder-led, proof-first, no rate cards, no junior
handoffs. The website itself (96+ Lighthouse, interactive 3D, AEO-structured)
is Exhibit A.

## Channels now

| Channel | Role | Cadence |
|---|---|---|
| Blog (seowithfaiz.com/blog) | Authority + AI-search citations | 2/wk drafted (Mon/Thu cloud), published Tue/Fri after editorial audit |
| Google Business Profile | Local + brand searches, freshness | 1/day via Buffer |
| Instagram (@seo_with_faiz) | Craft showcase, brand surface | 1/day via Buffer (branded card) |
| LinkedIn (seowithfaiz) | PRIMARY ICP channel | ✅ connected since 2026-07-09; first post drafted 2026-07-11, awaiting Faiz's approval before cadence starts |

## Conversion strategy — closing $1K–$5K/mo retainers with today's proof
### (added 2026-07-08 after honest proof assessment; all roles align to this)

Current proof supports craft-trust, not outcome-trust. Until outcome proof
exists, we compensate with five legitimate levers — never fabrication:

1. **Vertical wedge.** Lead with the two clusters we can actually prove:
   **boutique hospitality** (Button Eyes: booking funnels, WordPress, SEO)
   and **sports clubs/academies** (Little Stars, Hyderabad Globe FC).
   Content and angles should speak to these buyers by name — booking-funnel
   economics, seasonal demand, local+international guest search. Generalist
   angles remain, but the wedge gets priority.
2. **Teardown-as-proof.** The public audit pack model is the flagship demo.
   Content shows diagnosis quality (mini-teardowns of common patterns —
   anonymized/pattern-level, never naming a business negatively in public).
3. **Pilot-sprint framing.** All CTAs and copy may reference "engagements
   begin with a focused 30-day sprint — defined deliverables, month to
   month, no lock-in." (Still no prices.)
4. **Build-in-public receipts.** Publish this site's own real growth
   evidence as it accrues (GSC/analytics screenshots, AI-citation wins).
   Own-site results are proof nobody can dispute.
5. **Proof harvest (needs Faiz, listed under "asks").** Named testimonials
   from Little Stars + Hyderabad Globe FC; Google reviews on the GBP
   profile; free Clutch listing.

**Outbound (prepared-by-machine, sent-by-human):** the highest-converting
motion at this proof level is a personalized teardown sent to a hand-picked
hospitality/sports prospect. Automation may research and draft; Faiz sends.

## Current focus themes (strategist rotates these)

1. Boutique-hospitality wedge: booking funnels, hotel SEO, direct-booking
   economics (ties to Button Eyes case).
2. Sports-organization wedge: club/academy sites that recruit and retain
   (ties to Little Stars + HGFC).
3. The rebuild story: 96+ Lighthouse WITH a 3D WebGL hero (craft-proof).
4. AI search (AEO/GEO): how buyers' customers now find answers.
5. Platform truth: Shopify Plus vs Magento vs custom — candid fit guidance.

**(2026-07-11 note, not a reorder):** week-1 reach is still single digits
(1–9) per on-pipeline post, too thin to declare a top-quartile format —
holding rotation steady. Directionally, the AEO/buyer-education post
("Your customers stopped clicking. They started asking.") had the week's
best engagement rate (75%, n=4 reach) of anything in the approved pipeline;
worth one more AEO-pillar angle next week, not a pillar promotion yet.

**(2026-07-20 update):** two weeks running, the clear top performer is
case-study/proof-anchored content with a concrete CTA — not any one pillar.
07-13 LinkedIn (Hyderabad Globe FC rebuild) hit 65 reach/91 impressions,
the week's best by a wide margin; 07-13 Instagram (30-day-sprint pov, also
proof-anchored) hit 55 reach/1 share. Every other post this week sat in a
flat 3-4 reach band on Instagram regardless of pillar, so pillar rotation
still isn't the lever — format is. Per the optimization rule, 2 more
case-study-anchored angles are already staged next in QUEUE.md (Little
Stars Next.js build, another Button Eyes angle). Holding pillar rotation
otherwise.

**(2026-08-24 update — resuming after a ~5-week gap in the scheduled
roles):** no on-pipeline social/blog content published between 2026-07-20
and today. There is no fresh performance data this week, so the
case-study/proof-anchored-format finding from 07-20 is still the best
evidence on hand — while this run was in progress, the Social Manager role
resumed concurrently (live in this same working tree) and, per that
guidance, swapped a queued GBP-taps angle for the staged Little Stars
Next.js case-study angle for 2026-08-25 (see LOG.md / git history
2026-08-24). Good sign the loop is running again — holding pillar rotation
and the format-over-pillar finding from last data; worth confirming
tomorrow's post actually goes out and gets logged.

**(2026-09-04 deep technical/SEO audit — requested directly by Faiz, not
the routine weekly loop):** ran a full non-branded-keyword + competitor +
technical audit using GA4, live-site crawling (robots.txt, sitemap.xml,
raw HTML of homepage + a blog post), and SERP checks, because the real
Google Search Console connector is not authorized this session (Adspirer's
`google_search_console` tool reports "not connected" — see Asks). Headline
finding: **Organic Search delivered 7 sessions in the last 90 days**
(vs. Direct 204, Organic Social 33) — statistically zero, not a slow
ramp. The flagship blog post's exact unique title returns zero hits on a
live web search, meaning the site isn't surfacing even for its own
unindexed-competition title. Root-caused it to two compounding causes, one
now fixed:
1. **FIXED THIS RUN: `sitemap.xml` was stale since 2026-07-06.** 5 of the
   6 published blog posts (`answer-engine-optimization-guide`,
   `how-to-get-cited-by-chatgpt...`, `local-seo-that-turns-map-views...`,
   `recovering-after-a-google-core-update...`,
   `technical-seo-priorities-when-crawl-budget...`) were live (200,
   correctly linked from `/blog/index.html`) but **absent from the
   sitemap** — the file that tells Google what to prioritize crawling.
   Root cause: no script in `automation/blog/` ever writes to
   `sitemap.xml` — it was hand-authored once and never wired into the
   publish pipeline (`publish_validator.py` doesn't touch it). Added all 5
   missing URLs directly (root `sitemap.xml`, now 38 entries, valid XML) —
   but the pipeline gap is still open; see Asks.
2. **Not a technical-hygiene problem otherwise.** Verified directly against
   raw HTML (not the lossy AI-summarized fetch, which first mis-reported
   10 H1s by flattening h2/h3 sections — corrected via curl+grep): homepage
   has exactly 1 H1, correct canonical, meta description, Organization +
   WebSite JSON-LD; the audited blog post has BlogPosting + Person(author)
   + BreadcrumbList schema, a named byline (E-E-A-T), proper canonical, and
   ~1,300–1,500 words. robots.txt allows everything. Images ship
   width/height + lazy-loading. This is a **young-domain / zero-backlink
   problem, not a broken site** — the domain's oldest sitemap entries date
   to 2026-05-24, so it's ~3.5 months old with (per this session's checks)
   no external mentions found anywhere on the web.
3. **Competitive reality check (non-branded head terms):** ran live SERP
   checks on "Shopify Plus vs Magento enterprise 2026," "crawl budget
   optimization for ecommerce," and "AI Overviews SEO strategy 2026" — all
   three are owned by established DR40–70+ agencies (folio3, elogic,
   conductor, highervisibility, tripledart, yotpo, position.digital, etc).
   At current domain authority, competing on these head terms directly is
   not realistic short-term; the win condition is long-tail specificity +
   the AEO/GEO wedge (less saturated, and the only channel already
   converting in GA4 — "AI Assistant" delivered 1 session / 3 keyEvents,
   a better per-session conversion rate than anything else in the property,
   even accounting for the keyEvents tracking-bug caveat already on file).
   One externally-sourced fact worth building content around: pages with
   comprehensive JSON-LD are ~3x more likely to appear in AI Overviews, and
   fact density (not word count) is what correlates with AI citation —
   this site already ships the schema; almost no competitor content in
   the SERPs checked leads with that build-level specificity.
**(2026-09-04 correction, same day):** Faiz confirmed GSC is linked —
through GA4's native Search Console integration, not the standalone
Adspirer/Ahrefs connectors (both genuinely unauthorized this session,
confirmed by direct retry). GA4's `organicGoogleSearch*` metrics
(`Clicks`/`Impressions`/`ClickThroughRate`/`AveragePosition`) pulled real
data and **materially revise the "statistically zero" framing above**: the
site does have real, if thin, Google Search presence — 259 impressions,
10 clicks, 3.86% CTR over May 1–Sep 4 (67 days with any signal). The
GA4-session-based "7 sessions" figure undercounted because most impressions
never convert to a countable session at this volume. **The sharper,
genuinely new finding: impression-weighted average position has gotten
WORSE over time, not better** — 6.0 (13 days, May–June) vs. 26.7 (28 days,
August) — and there hasn't been a single click since 2026-08-20 despite
continued impressions. That's the opposite of the normal young-domain
trajectory (should improve as Google gains trust) and worth investigating
directly in GSC's own UI, where query-level detail is visible — GA4's link
only exposes site-wide daily aggregates via the Data API (no `query`
dimension came back from metadata, and pairing these metrics with
`landingPage` or any dimension besides `date` returns "incompatible").
**Caveat on the trend:** daily volume is often 1-9 impressions, so a single
matched query can swing one day's "average position" by 50+ points — real
pattern, but noisy; the timing loosely overlaps Google's Aug 18-21 2026
spam update (already a queued blog angle) but the degradation was visible
before that window too, so treat as a hypothesis, not a confirmed cause.
**Ask added: Faiz should pull the query-level GSC report directly (Search
Console UI → Performance → Search results, export or screenshot) so the
team can see WHICH queries are losing position** — that's the one layer
this system still cannot reach.

4. Found and fixed one smaller thing in passing: `/case-studies/*`,
   `/services/web-design-development`, and `/mentions` all 404 without the
   `.html` extension (only `.html` resolves) — internal links are all
   correctly `.html`-suffixed so this isn't self-inflicted crawl waste, but
   GA4 shows historical pageviews on the extensionless paths too, meaning
   something external once linked the bare form. `_redirects` was
   deliberately left without an index-redirect rule after a prior
   documented redirect-loop incident (see `_redirects` comments +
   `worker.js`), so a bare extensionless→`.html` rule needs a careful
   worker-level check, not a blind `_redirects` add — logged as an Ask for
   a dev pass rather than changed blind this run.

**(2026-09-07 weekly review):** pipeline shipped GBP+LinkedIn on schedule
4 days this week (09-03, 09-05, 09-06, 09-07), rotating buyer-education →
behind-studio → platform-truth per standing rule. All three posts with
metrics landed in a flat 20-26 reach band — too thin to call a pillar
winner or loser, holding rotation. GA4 sessions roughly doubled
week-over-week (66 vs. 32: Direct 47, Referral 7, Organic Social 6,
Unassigned 6), homepage taking most of it — a real if small uptick — but
`keyEvents` is still the unfixed `swf_consent` artifact (standing ask since
07-20). Gmail: 0 genuine contact-form/strategy-call inquiries again, but
one real positive signal outside the ledger — Faiz had a live call with a
prospect ("Hebe") and sent a full plan follow-up 2026-09-06 (see new Ask).
Rising sessions + zero inquiries is now the established pattern every
logged week — per the optimization rule, the bottleneck is the offer/CTA
surface, not reach or volume; worth a dedicated CTA/booking-page review
rather than more content volume. QUEUE.md holds 14 unused social + 16
unused blog angles, well above the ≥10/≥5 floor — no refill needed.

**(2026-09-14 weekly review):** **platform-truth is now a confirmed
2-week top-quartile pillar** — this week's LinkedIn "Shopify or Magento?"
post hit 72 reach/110 impressions/1 reaction/1 comment, the studio's
best-performing post in a month, by a wide margin over the same week's
other two posts (WebGL globe craft-proof, 18 reach; core-update-recovery
buyer-education, 2 reach). Per the standing optimization rule, 2 more
platform-truth angles are now queued (Wix vs. custom-build, WordPress vs.
Magento) — see QUEUE.md. The weak core-update post isn't a pillar signal:
it's the 4th and final atomization of the same blog post, and every queued
core-update line is now used, so buyer-education needs a fresh angle next,
not a pause. GA4 sessions fell week-over-week for the first time on record
(43 vs. 66: Direct 31, Organic Social 5, Organic Search 3, AI Assistant 2,
Unassigned 2) — homepage still dominant (32 of 43); not enough signal yet
to call a trend, but worth watching next week. `keyEvents` remains the
unfixed `swf_consent` artifact (standing ask since 07-20, now 8 weeks
open). Gmail: 0 genuine inquiries again; the "Hebe" prospect still hasn't
replied 8 days after Faiz's 09-06 proposal — escalating the follow-up ask.
Buffer only shipped on 3 of 7 days this week (09-07, 09-08, 09-12), a
3-day gap 09-09→09-11 — worth confirming the cadence didn't silently
lapse. Instagram is disconnected in Buffer for a 6th consecutive run (no
post since 08-28, 17 days). One genuine piece of good news: the
extensionless-URL 404s flagged 09-04 are now resolved (curl-verified 200
across the board) — closing that ask. One escalation: the blog
compliance-gate regression flagged 08-24 hasn't just persisted, it's
worsened — Content Factory added 6 fresh AI-search drafts this run (found
uncommitted, now committed as pipeline output) and all 18 drafts in
`blog/drafts/` (12 old + 6 new) sit at `needs_revision`, 0 `ready` — the
blog channel has published nothing new since 07-14, now 8+ weeks.

## Asks awaiting Faiz (the strategist re-surfaces these weekly)

- [ ] **ESCALATED 2026-09-14 — the "Hebe" prospect still hasn't replied,
  now 8 days after Faiz's 2026-09-06 proposal.** Checked Gmail directly
  this run (thread `alimdmoaz@gmail.com` / "Your Hebe website + local SEO
  plan (as promised)") — no reply found. This was the closest thing to a
  real pipeline deal; the 9 July teardowns went cold after a similar
  silent gap. Recommend a short, low-pressure follow-up this week before
  it does the same.
- [ ] **UPDATED 2026-09-04 (same day) — GSC IS reachable via GA4's link;
  the gap is narrower than first thought.** Correction to the original
  version of this ask: Faiz confirmed GSC is connected through GA4, and
  `organicGoogleSearch*` metrics (Clicks/Impressions/CTR/AveragePosition)
  do return real data that way — see the focus-themes correction note
  above (259 impressions/10 clicks/67 days, average position worsening
  6.0→26.7 May-June vs. August). What's still missing: **query-level
  detail** — GA4's Data API only exposes site-wide daily aggregates for
  these metrics (no `query` dimension, and no pairing with `landingPage`).
  To see WHICH queries are losing position, Faiz needs to pull that
  directly from Search Console's own UI (Performance → Search results →
  export). Separately, the Adspirer standalone `google_search_console`
  tool and the Ahrefs MCP's GSC-integration/Site Explorer/Keywords
  Explorer/Rank Tracker/Site Audit tools are still genuinely unauthorized
  (`"not connected"` / `"Insufficient plan"`, confirmed by direct retry
  after Faiz's first reconnect attempt) — not blocking now that the GA4
  path works for aggregates, but still worth fixing for query-level access
  and competitor data.
- [ ] **NEW, P0 — `sitemap.xml` will go stale again on the next blog
  publish unless the pipeline is fixed.** This run manually added the 5
  blog posts missing from the sitemap (see focus-themes note above), but
  `automation/blog/publish_validator.py` has no step that touches
  `sitemap.xml` at all. Needs an engineering fix: append each newly
  published post's `<url>` block to `sitemap.xml` as part of the
  `--publish` step (or generate the sitemap from `blog/posts/*.html` on
  every publish instead of hand-maintaining it). Otherwise every future
  post repeats this exact bug.
- [x] ~~extensionless URLs 404 site-wide~~ — **resolved, confirmed
  2026-09-14**: `/case-studies/button-eyes-resort`, `/mentions`, and
  `/services/web-design-development` all curl-verified 200 (no `.html`
  needed) this run. Whatever fix landed (not attributable to this pipeline
  — no `_redirects`/`worker.js` commit found in this session's git log),
  it worked. No further action needed.
- [x] ~~Instagram channel disconnected in Buffer~~ — **resolved 2026-09-17**:
  after 20 days dark / 9 consecutive skipped runs (first flagged 2026-09-05),
  Faiz reconnected it from the Buffer dashboard. Confirmed via `list_channels`
  (`isDisconnected: false`) the same day, and a matching Wix platform-truth
  Instagram post (mirroring today's already-shipped GBP/LinkedIn angle) was
  generated and scheduled for 2026-09-18 17:30 IST — the first Instagram
  content since 08-28. No fresh time/format signal exists yet (only the 2
  stale pre-disconnect posts on record), so the next few runs should treat
  Instagram's reach/engagement data as a fresh baseline, not a continuation
  of the pre-outage numbers.
- [ ] **ESCALATED 2026-09-14 — blog channel has now published nothing new
  in 8+ weeks, and the drafts backlog got worse, not better.** First
  flagged as a regression 2026-08-24 (12/12 backlog drafts stuck
  `needs_revision`). This run found 6 more Content Factory drafts sitting
  uncommitted in the working tree (committed as pipeline output this run —
  see LOG-equivalent note in METRICS.md) — all 6 are also
  `needs_revision`, bringing the backlog to **18/18 needs_revision, 0
  ready**. The compliance-gate fix from 07-10
  (`automation/blog/{content_builder,draft_generator,compliance,
  humanization,intent_content,intent_research,publish_validator}.py`)
  either regressed again or was never sufficient for this newer batch of
  AI-search-cluster drafts. This is outside the Growth Strategist's remit
  but is now the single biggest gap in the content engine — the "Authority
  + AI-search citations" channel goal has been fully stalled for 2 months.
  Needs an engineering/editorial pass on why every draft fails the gate,
  not just a re-run of the pipeline.
- [ ] **NEW, URGENT (partially resolving live): the Editor-in-Chief,
  Social Manager, Prospector, and Growth Strategist scheduled roles went
  silent for ~5 weeks** (2026-07-20 → 2026-08-24 — LOG.md's last entry
  before today was 07-20; no blog/GBP/Instagram post shipped in that
  window). **Correction to an earlier draft of this note:** the blog-draft
  GitHub Action (`Automate blog draft pipeline updates`) did NOT stop —
  git history shows it ran every 3-4 days the whole time (2026-07-20,
  07-23, 07-27, 07-30, 08-03, 08-06, 08-10, 08-13, 08-17, 08-20, 08-24) —
  it just never produced a draft that cleared the compliance gate (see the
  next ask). The roles that actually went dark are the ones that run on
  this Claude-Code-scheduled-task loop, not GitHub Actions. **While this
  run was in progress, that loop appears to have resumed on its own** — a
  concurrent Social Manager-style commit landed mid-run
  (`b37c662`/`f01aabb`, 2026-08-24, branded cards for 2026-08-25) and
  PROSPECTS.md picked up fresh Gmail reply-checks dated today. Worth
  Faiz confirming tomorrow's (08-25) posts actually go out and get logged,
  and checking why the loop paused for 5 weeks in the first place so it
  doesn't happen silently again.
- [ ] **NEW: 2 off-brand LinkedIn posts went out 2026-08-17** (via Buffer,
  outside this pipeline) — "Stop chasing ghost buttons in Google Tag
  Manager!" and "The Google Ads August 17th Update is Here..." Both read
  like generic stock marketing-agency content: 12+ hashtags each, heavy
  emoji (📉🛑👻💻), "Let's discuss in the comments! 👇" comment-bait, and
  zero connection to SWF's positioning, wedge, or case studies — they'd
  fail nearly every check in the Elite Audit Protocol (Voice, Positioning,
  Compounding). Given the identical pattern to the 2026-07-05 Instagram
  false-alarm (Faiz posting manually, not a compromise — see
  `swf-instagram-unauthorized-posts-incident` memory), this is most likely
  Faiz posting by hand while the pipeline was down. Needs his confirmation
  either way; if manual, worth deciding whether to leave them, edit them
  toward brand guardrails, or delete — his call, not corrected here.
- [x] ~~Blog draft backlog regressed, and the bot is running, not
  stalled~~ — **superseded 2026-09-14 by the escalated entry above** (18/18
  now `needs_revision`, up from 12/12 on 2026-08-24). Same root cause,
  worse now; tracking under the escalated ask instead of duplicating here.
- [ ] **GA4 tracking bug still unresolved, one month later.** First flagged
  2026-07-20: `keyEvents` is 100% the `swf_consent` cookie-banner-click
  event; the property's real configured conversions (`purchase`,
  `close_convert_lead`, `qualify_lead`) fired zero times again this week.
  Every "X sessions" report from this system remains sessions-only data
  until a genuine contact-form-submit or strategy-call-booked event is
  marked as the GA4 key event.
- [ ] **Prospector's 3 unsent drafts are now 5+ weeks stale.** 1824 House
  Inn + Barn, Locker Soccer Academy, and Steamboat Inn have sat at
  `drafted` in `PROSPECTS.md` since 2026-07-16 without being sent. The 9
  sent 2026-07-12 got zero replies after a follow-up — recommend either
  sending these 3 now (the teardown findings should still be accurate) or
  discarding them and having the Prospector re-verify before a fresh
  batch, since site content can change over 5+ weeks.
- [x] ~~Unauthorized Instagram posts~~ — **resolved/corrected 2026-07-09: Faiz
  confirmed he posted these himself**, not a compromise. Leaving one note
  for awareness, not urgency: the 8 posts (2026-07-05–06, paid-ads/PPC
  "teardown" copy) still contain two price mentions ("$500 SEO retainer",
  "$10k a month hiding in your ad account") and "Comment X for an auto-DM"
  bait, which conflict with the studio's own no-prices and no-comment-bait
  rules if judged by the same Elite Audit Protocol as pipeline content.
  No action needed unless Faiz wants them edited/removed — his call.
- [x] Blog draft backlog — **addressed 2026-07-10**: the compliance-gate bug
  that stuck every draft at `needs_revision` was fixed; 9 of 14 backlog
  drafts now pass, 2 published (technical-SEO priorities, ChatGPT-citation
  guide). Remaining ask: 7 ready-but-unpublished AEO/GEO-cluster drafts are
  deliberately throttled to ≤1/week to avoid keyword cannibalization, and 5
  stale/duplicate stubs are annotated `needs_revision` awaiting a human
  decision to delete from `blog/drafts/` — please confirm those 5 can go.
- [ ] **New: blog cadence has stalled.** No post has published since
  2026-07-14 (Friday 07-17's editorial slot appears to have been skipped),
  and all 12 remaining files in `blog/drafts/` are now `review_status:
  needs_revision` — zero are `ready`. The Content Factory/Editor-in-Chief
  roles need either fresh Mon/Thu drafts or a revision pass on the backlog
  to keep the 2/week cadence; this is outside the Growth Strategist's
  remit but is blocking the "Authority + AI-search citations" channel goal.
- [ ] Request named testimonials: Little Stars, Hyderabad Globe FC.
- [ ] Ask 2–3 real contacts for Google reviews on the GBP profile.
- [x] Create free Clutch.co profile — submitted 2026-07-08, Clutch is reviewing before publishing (confirmation email received).
- [x] ~~LinkedIn draft awaiting approval~~ — **resolved by 2026-07-19**: the
  2026-07-10 draft is no longer present in Buffer (0 drafts across all
  channels as of this run's queue check); LinkedIn has been on the daily
  scheduled-live cadence since 2026-07-13 per LOG.md. No action needed.
- [ ] Instagram → Facebook Page link — still not fully propagated, 3rd
  consecutive week. `get_instagram_accounts(act_2089451385293163)` again
  returns 0 accounts, while the direct-account-id path continues to return
  real data (reach 74, profile views 6, last_7d). Reproduced 3 weeks
  straight now — either file a Meta support ticket, or since the working
  path is sufficient for our reporting needs, formally deprioritize this
  and stop re-flagging it weekly.
- [ ] **Prospector outreach is still mostly stalled.** Of 12 teardown
  drafts total, 9 are `sent` (2026-07-12) with zero replies after a
  2026-07-16 followup, and 3 newer ones (1824 House Inn + Barn, Locker
  Soccer Academy, Steamboat Inn) have sat at `drafted`, unsent, since
  2026-07-16. Recommend sending those 3 this week — and if the 9 sent
  keep getting zero replies, that's a signal to test a different opening
  (e.g. the warm-intent AI-search angle below) rather than just more volume.
- [x] **RESOLVED — the "near-zero GA4 traffic" flag from last week was a
  tracking-config bug, not a demand problem.** GA4 sessions are up to 77
  this week (Direct 53, Organic Social 13, Unassigned 9, Organic Search 2),
  but the property's `keyEvents` metric (40 this week) is 100% the
  `swf_consent` event — a cookie-consent-banner click — confirmed via an
  eventName breakdown. The property's actual configured conversion events
  (`purchase`, `close_convert_lead`, `qualify_lead`) fired **zero times**
  all week. **This needs Faiz's attention**: there is currently no real
  lead-conversion signal in GA4 at all. Either mark a genuine event (a
  contact-form submit, a "book a strategy call" click) as the key event, or
  every future GA4 "conversions" number this system reports is meaningless.
  Until fixed, treat GA4 as sessions-only data — the Gmail inquiry count
  is the only trustworthy lead signal.
- [ ] **New: Faiz's LinkedIn profile is getting flooded with "new lead"
  marketplace notifications — worth a judgment call, not urgent.** ~20
  unread emails this week from LinkedIn's Service Marketplace ("a new lead
  is available in [Indian city]"), all for one-off gigs from individuals,
  not businesses — e.g. "Digital Marketing Manager... looking for help,"
  budget type "one time need." These are tied to Faiz's personal
  profile having "Providing services" enabled, not to seowithfaiz.com, and
  don't match the enterprise US/CA/AU/EU ICP. They're not inquiries against
  our north-star metric (none counted as such this week) — Faiz's call
  whether to keep them on for occasional relevant overflow work or turn the
  marketplace-lead notifications off to cut inbox noise.

## Standing rules

- Never two consecutive posts from the same pillar.
- Every piece passes the 7-check Elite Audit Protocol before shipping.
- No prices, no invented proof, no buttoneyes.in links, founder voice.
- Kill switch: `marketing/PAUSE` file stops everything.
