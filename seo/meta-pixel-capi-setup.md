# Meta Pixel + Conversions API — setup for seowithfaiz.com

> Built 2026-07-17. Pixel events go through the **web GTM container**
> (`GTM-KQ9KNHN2`); the Conversions API (CAPI) is **server-side** and runs in
> `worker.js` — a client-side GTM container cannot send CAPI. Best practice is
> both, sharing an `event_id` so Meta de-duplicates.

## Prerequisite done in-repo
- CSP (`_headers`) now allows `connect.facebook.net` (script) + `www.facebook.com`
  / `connect.facebook.net` (connect). Without this the Pixel is silently blocked.

## Event mapping — only fire events that map to real actions
Meta penalizes low-quality/empty events, so don't create phantom triggers.

| Meta event | Real action on this site | Fire via |
|---|---|---|
| **Lead** | Contact-form submit → redirect to `/thank-you.html?sent=1` | GTM Pixel **+** Worker CAPI |
| **ViewContent** | Views of `/services/*`, `/case-studies/*`, `/blog/posts/*` | GTM Pixel |
| **Contact** | Click `mailto:win@seowithfaiz.com` or `https://wa.me/916281367104` | GTM Pixel |
| **Schedule** | Click "Book a strategy call" CTA (`.nav-cta`, `[data-dynamic-cta]`) — *intent, not a confirmed booking* | GTM Pixel (optional) |
| **Search** | No meaningful site search — **skip** | — |
| **SubmitApplication** | No application flow — **skip** (Lead covers the inquiry) | — |

## GTM setup (web container GTM-KQ9KNHN2)

### 0. Consent (respect the existing banner)
The site already runs Consent Mode v2 (`ad_storage` denied by default, granted
when a visitor accepts marketing in the banner; the banner also pushes a
`swf_consent` dataLayer event with `ad_consent`). Gate every Meta tag on it:
on each Meta tag → **Consent Settings → Require additional consent for: `ad_storage`**.
That makes tags wait until the visitor opts in — no extra trigger needed.

### 1. Base Pixel (PageView)
- Tag → New → **Facebook Pixel** (gallery template by *facebookincubator*; if you
  prefer, a Custom HTML tag with Meta's base snippet also works).
- Pixel ID: paste your Pixel ID.
- Event Name: **PageView** (standard).
- Consent: require `ad_storage`.
- Trigger: **Initialization - All Pages**.

### 2. ViewContent
- New Facebook Pixel tag, use existing Pixel ID, Event: **ViewContent**.
- (Optional param) `content_name` = `{{Page Path}}`.
- Trigger: **Page View**, fire when **Page Path** matches RegEx
  `^/(services|case-studies|blog/posts)/`.

### 3. Contact
- New tag, Event: **Contact**.
- Trigger: **Click - Just Links**, fire when **Click URL** matches RegEx
  `^(mailto:|https://wa\.me/)` (enable "Wait for Tags" so the mailto/WhatsApp
  navigation doesn't cancel the tag).

### 4. Lead (the money event)
- New tag, Event: **Lead**.
- Trigger: **Page View**, fire when **Page Path** equals `/thank-you.html`
  (tighten with **Page URL** contains `sent=1` if you want submit-only).
- This is also sent server-side via CAPI (below) — dedup handles the overlap.

### 5. Schedule (optional, intent-level)
- New tag, Event: **Schedule**.
- Trigger: **Click - All Elements**, fire when the clicked element matches CSS
  `.nav-cta, [data-dynamic-cta]`. Treat as upper-funnel intent, not a booking.

Then **Preview** (GTM debug) → accept the cookie banner → confirm each event
shows in Meta **Events Manager → Test Events**, and **Publish** the container.

## Customer-information parameters (the list from Events Manager)
- **Browser Pixel** auto-captures `fbp`/`fbc` cookies; Meta reads **client IP +
  user agent** server-side from the `/tr` call. You generally don't pass PII
  client-side here (the thank-you page doesn't hold the email).
- **CAPI (Worker)** supplies the hashed **email** + IP + UA for the Lead event —
  that's what covers the Email / IP / User-Agent matching params Meta listed.
  Together the two give Meta strong match quality.

## CAPI (server-side) — status & to activate
`worker.js` already has `sendMetaEvent()` using `META_PIXEL_ID` + `META_CAPI_TOKEN`.
It currently fires on CRM status changes (call → Schedule, won → Purchase). To
make it also send **Lead on form submit** and **de-duplicate with the browser
Pixel**, two small changes are needed (offered separately, not hardcoded yet):
1. Add `sendMetaEvent(lead, 'Lead')` in the contact-submit path.
2. Generate an `event_id` in the browser at submit, pass it in the POST body,
   and use the same value for the Pixel `eventID` and the CAPI `event_id`.
Secrets: the tokens in `APIs.env` must also be pushed to the Worker
(`wrangler secret put META_PIXEL_ID` / `META_CAPI_TOKEN`) — APIs.env is local
only; the Worker reads Cloudflare secrets.
