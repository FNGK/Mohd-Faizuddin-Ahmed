> **SUPERSEDED (2026-07-12):** Faiz went with a client-side **GTM container
> (`GTM-KQ9KNHN2`)** instead — installed site-wide via `automation/inject_gtm.py`
> + `assets/js/gtm-loader.js`, consent-gated by the banner in `site.js`. Configure
> GA4 + the LinkedIn Insight Tag *inside GTM* now. This Zaraz guide is retained
> only as a fallback if you later reconsider edge/server-side tagging.

# Cloudflare Zaraz — server-side tracking + consent setup

> Built 2026-07-12. This is the dashboard-side checklist to turn on GA4 +
> LinkedIn tracking through **Cloudflare Zaraz** (edge/server-side tag loading),
> gated by the custom consent banner already shipped in `assets/js/site.js`.
>
> **Why Zaraz here:** the site is on Cloudflare, so Zaraz loads tags at the
> edge from a same-origin path (`/cdn-cgi/zaraz/`). That gives first-party
> cookies (longer-lived under Safari/Firefox tracking prevention), ad-blocker
> resistance, and less client-side JS — the "cookie-resilient / server-side"
> goal — without standing up a separate Google sGTM server.

## ⚠️ Honest caveat (don't skip)
Server-side tagging does **not** remove the legal need for consent. GDPR/ePrivacy
(UK/EU/Ireland) still require prior opt-in for analytics + advertising, and
CCPA/CPRA (California) requires notice + opt-out of "sharing". That's exactly why
the consent banner exists and why tags below are set to **require consent**.
Since the LinkedIn campaign targets US/UK/CA/AU/IE, the banner is mandatory once
these tags are live.

## Current state (verified 2026-07-12)
- GA4 (`G-LQZ72RK5LM`) is **not actually firing** on the live site — no gtag/GTM
  loader is present in the served HTML. This is why GA4 shows ~0 sessions.
  Zaraz will be GA4's first working install.
- No LinkedIn Insight Tag present.
- Consent banner: shipped in `site.js`, CSP-safe, brand-themed, **inert until
  Zaraz is enabled** (it only shows once `window.zaraz` is present).

## Dashboard steps (Cloudflare → your domain → Zaraz)
1. **Enable Zaraz** for `seowithfaiz.com` (free tier covers well beyond current
   traffic).
2. **Add tool → Google Analytics 4.** Measurement ID: `G-LQZ72RK5LM`. Enable
   automatic pageviews. (Zaraz can also forward the custom events `site.js`
   already emits: `cta_click`, `outbound_click`, `generate_lead`.)
3. **Add tool → LinkedIn Insight Tag.** Partner ID: get it from LinkedIn
   Campaign Manager → **Analyze → Insight Tag → "I will install the tag myself"**
   → copy the numeric **Partner ID**. (The Insight Tag also needs the domain
   allow-listed in Campaign Manager.)
4. **Zaraz → Consent.** Turn **Consent Management ON**. Create two purposes:
   - **Analytics** → assign the GA4 tool to it.
   - **Advertising / Marketing** → assign the LinkedIn tool to it.
5. **Turn the default Zaraz consent modal OFF** (we use the custom banner).
   Keep "tools respect consent" ON so nothing fires before opt-in.
6. **Copy each purpose's ID** (Zaraz shows a purpose ID per purpose). Paste them
   into `assets/js/site.js`:
   ```js
   var CONSENT_PURPOSES = { analytics: "<analytics-purpose-id>", advertising: "<advertising-purpose-id>" };
   ```
   Commit + push. (Until you do this, the banner falls back to Zaraz
   `setAll()` — Accept-all grants everything, Reject denies everything, but the
   granular Analytics-only / Marketing-only choice won't map precisely.)

## CSP
No change needed to `_headers` for Zaraz itself — it loads from same-origin
`/cdn-cgi/zaraz/`. GA4's `connect-src` is already allow-listed. **If** the
LinkedIn tool fires a client-side pixel (check the browser Network tab for
`px.ads.linkedin.com`), `img-src` already permits it (`https:`); only add
`https://px.ads.linkedin.com` to `connect-src` if the console reports a block.

## Verify after enabling
1. Load the site in a fresh/incognito window → the consent banner appears.
2. **Accept all** → GA4 **Realtime** shows your visit; Zaraz "Monitoring"/log
   shows GA4 + LinkedIn firing; a first-party `swf_consent` cookie is set.
3. **Reject** → confirm neither tool fires (Zaraz log empty, no GA4 realtime).
4. Confirm the "manage your cookie choices" link on `/privacy/` re-opens the
   banner.

## What this unblocks
- Real GA4 data at last (fixes the zero-data problem in `marketing/METRICS.md`).
- LinkedIn conversion tracking + retargeting for the ads campaign
  (`marketing/LINKEDIN-ADS-CAMPAIGN.md`).
- First-party, consent-gated, ad-blocker-resilient measurement.
