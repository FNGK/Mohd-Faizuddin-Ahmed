# Cloudflare redirect rules (seowithfaiz.com)

GitHub Pages URLs on `fngk.github.io` are redirected in-repo via `assets/js/canonical-redirect.js` and `404.html`. Cloudflare rules below apply only to your custom domain zone.

## Required rules (Bulk Redirects or Redirect Rules)

Create these in **Cloudflare Dashboard → seowithfaiz.com → Rules → Redirect Rules** (or Bulk Redirects).

### 1. www → apex (301)

| Field | Value |
|-------|--------|
| If | Hostname equals `www.seowithfaiz.com` |
| Then | Static redirect to `https://seowithfaiz.com${http.request.uri.path}${http.request.uri.query}` |
| Status | 301 |
| Preserve query string | Yes |

Expression (Redirect Rules):

```
(http.host eq "www.seowithfaiz.com")
```

Target URL:

```
https://seowithfaiz.com${uri.path}${uri.query}
```

### 2. Force HTTPS on apex (if not already)

Usually enabled via **SSL/TLS → Edge Certificates → Always Use HTTPS**. No separate rule needed if that toggle is on.

### 3. Optional: strip `index.html` (301)

| If | URI Path ends with `/index.html` |
| Then | Redirect to same path without `index.html` |

Example target: `https://seowithfaiz.com${uri.path}` with rewrite to remove trailing `index.html` (use Cloudflare “Replace” dynamic redirect or a single Page Rule).

## DNS (custom domain on GitHub Pages)

For `seowithfaiz.com` serving GitHub Pages through Cloudflare:

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| CNAME | `@` | `fngk.github.io` | Proxied (orange cloud) |
| CNAME | `www` | `fngk.github.io` | Proxied |

In GitHub: **Settings → Pages → Custom domain** = `seowithfaiz.com` (and optionally `www.seowithfaiz.com`).

## What Cloudflare cannot do

- Redirect `https://fngk.github.io/Mohd-Faizuddin-Ahmed/*` — that hostname is on GitHub, not your zone. Use the repo redirect script + `404.html` instead.

## Verify after deploy

```bash
# GitHub Pages (should redirect in browser; HTTP may still be 200 from GitHub)
curl -I "https://fngk.github.io/Mohd-Faizuddin-Ahmed/contact/index.html"

# Apex
curl -I "https://seowithfaiz.com/contact/index.html"

# www should 301 to apex
curl -I "https://www.seowithfaiz.com/"
```

In Chrome: open `https://fngk.github.io/Mohd-Faizuddin-Ahmed/index.html` — address bar should become `https://seowithfaiz.com/` (or `/index.html`).
