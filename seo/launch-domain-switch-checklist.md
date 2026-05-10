# Launch-Day Domain Switch Checklist (`seowithfaiz.com`)

Use this checklist when moving from GitHub Pages to production hosting.

## 1) Infrastructure

- Provision SSL certificate for `seowithfaiz.com` and `www.seowithfaiz.com`.
- Enforce HTTPS with 301 redirect from HTTP to HTTPS.
- Configure canonical host strategy (`seowithfaiz.com` or `www`) and redirect the other.

## 2) Metadata and Canonicals

- Replace all canonical URLs from GitHub URLs to `https://seowithfaiz.com/...`.
- Update Open Graph and Twitter URLs/images to production domain.
- Update structured data `url`, `@id`, and `mainEntityOfPage` fields.

## 3) Crawl and Indexing

- Update `robots.txt` sitemap URL to production domain.
- Regenerate `sitemap.xml` with production URLs only.
- Submit production sitemap in Google Search Console and Bing Webmaster Tools.

## 4) Redirect and Link Safety

- Set 301 redirects from old GitHub Pages URLs to production URLs where possible.
- Verify no internal links still point to GitHub URLs.
- Run a full broken-link check before and after DNS cutover.

## 5) Analytics and Tracking

- Keep GA4 tag active and validate pageview tracking after migration.
- Add conversion events for form submissions and key CTA clicks.

## 6) Post-Launch Monitoring (First 14 Days)

- Monitor crawl errors and indexing anomalies daily.
- Track organic landing page shifts and branded query trends.
- Validate all forms, CTAs, and key service pages on mobile and desktop.
