# LinkedIn Ads — Campaign Kit #1 (Boutique Hospitality · Lead-Gen)

> Built 2026-07-12. This is a **paid** campaign kit — the ONE deliberate
> exception to the studio's organic-only default, authorized by Faiz on
> 2026-07-12. Everything here is prepared so launch is a short, deliberate
> step once the blockers below clear. No spend has been committed.

## ⚠️ Blockers before this can launch (owner-side)
1. **Ad account `551722756` is on `BILLING_HOLD`** — add a payment method in
   Campaign Manager. Nothing serves until this clears.
2. **Pick ONE Company Page** and complete it (logo, description, cover). Two
   empty duplicates exist: `SEO with Faiz` **135146531** (vanity `seowithfaiz`)
   and **135146282** (vanity `seo-with-faiz`, the one the ad account is tied to).
   Recommend keeping the one tied to the ad account and deactivating the other.
3. **Create the Lead-Gen Form** in Campaign Manager using the spec below
   (the ads connector cannot build the form itself).

Done on the studio side: privacy page (`/privacy/`), ad creative, ad copy,
targeting spec (below).

## Campaign structure
- **Objective:** Lead Generation
- **Ad format:** Single Image (Sponsored Content)
- **Sponsoring Page:** the completed Company Page (see blocker 2)
- **Bid:** Maximum delivery (let LinkedIn optimize) for the first test
- **Budget posture:** small validation test — set the exact daily figure at
  launch. (LinkedIn min is ~$10/day; expect $8–15+ per click for this audience.
  Judge on **cost-per-lead**, not clicks.)
- **Schedule:** run continuously; review after ~2 weeks or ~30 leads,
  whichever first.
- **Status at creation:** PAUSED (never auto-launch).

## Targeting spec — Boutique Hospitality wedge
Verified LinkedIn targeting URNs (pulled live 2026-07-12, account 551722756):

**Locations (include, OR):**
- United States — `urn:li:geo:103644278`
- United Kingdom, Canada, Australia, Ireland — add by name in the location
  typeahead (each resolves to its own geo URN).

**Industry (include):**
- Hospitality — `urn:li:industry:31`
- Also add *Leisure, Travel & Tourism* by name (broadens to resorts/inns not
  tagged "Hospitality").

**Job titles (include, OR):**
- Owner — `urn:li:title:1`
- Co-Owner — `urn:li:title:195`
- General Manager — `urn:li:title:17`
- Marketing Director — `urn:li:title:63`
- Director of Sales & Marketing — `urn:li:title:184`
- Add by typeahead: *Revenue Manager*, *Founder*, *Innkeeper* (if present).

**Company size (narrow):** 11–50 and 51–200 (boutique operators; skip 1–10 to
cut solo/side-projects, and 500+ to cut chains). Pick from the dropdown.

**Language:** English.
**Audience Expansion / Predictive audiences:** OFF for the first test (keep the
signal clean).

> ⚠️ Audience-size number: LinkedIn only reports a count for a **saved
> campaign's** targeting (min 300 members to run). We deliberately haven't
> created the campaign yet, so there's no live number to quote. Industry
> (Hospitality) + these titles across 5 English-speaking countries should clear
> the 300 floor comfortably; confirm the exact count in Campaign Manager's
> Forecasted Results panel when you build it (it's shown live as you add facets).

## Lead-Gen Form spec (build in Campaign Manager → Assets → Lead gen forms)
- **Form name (internal):** Boutique Hotel — Free Site Teardown
- **Headline:** Free 10-minute teardown of your hotel's website
- **Details:** Tell me where to send it. I'll record a 10-minute video
  walkthrough of your website — the three fixes I'd make first to win back
  direct bookings and get you found in AI search. No pitch, no cost.
- **Fields to collect** (keep short — every extra field lowers completion):
  - First name (prefilled)
  - Work email (prefilled)
  - Company name (prefilled)
  - Custom question — short text: **"Your website URL"**
- **Privacy policy URL:** https://seowithfaiz.com/privacy/
- **Custom consent checkbox (optional but recommended):** "I'd like Faiz to
  review my site and email me the teardown." (unchecked by default)
- **Confirmation / thank-you message:** Thanks — I'll review your site and send
  your teardown video within 3 business days, to the email you entered.
- **Confirmation CTA:** "See recent work" → https://seowithfaiz.com/case-studies/

## Tracking status (2026-07-13, live-verified)
- GTM `GTM-KQ9KNHN2` live site-wide; GA4 `G-LQZ72RK5LM` firing (first real data
  collection started today); **LinkedIn Insight Tag live — partner ID `10541097`**
  (`px.ads.linkedin.com/collect` verified firing post-consent); Conversion
  Linker published. Consent-gating verified end-to-end (fresh visitor → banner
  → accept → tags fire; CSP clean).
- Server-side CAPI lead conversion `29401001` wired in `worker.js` (pending
  `LINKEDIN_CONVERSIONS_TOKEN` secret). Insight Tag now also enables a
  URL-based conversion on `/thank-you.html` + website retargeting audiences.

## Ad creative
- **Image:** `assets/social/linkedin-ad-hospitality-teardown.png` (1200×627)
- **Introductory text:**
  Most boutique hotels quietly lose direct bookings — to OTAs taking 15–25%,
  and to a website guests (and now AI assistants) can't quite find. I'll show
  you exactly where. Request a free 10-minute teardown of your site: the 3
  fixes I'd make first. No pitch.
- **Headline (under image):** Free 10-minute website teardown for boutique hotels
- **CTA button:** Sign Up
- **Destination:** the Lead-Gen Form above

## Guardrails carried over
- No prices of ours anywhere (the "15–25%" is the *OTA's* commission, not our fee).
- No buttoneyes.in links.
- First-person founder voice.
- This is the only sanctioned paid channel; all other channels stay organic.
