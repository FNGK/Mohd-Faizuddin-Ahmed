# Cloudflare redirect rules (seowithfaiz.com)

Hosting is **Cloudflare Pages**. Redirects are split between the repo and the dashboard.

## In repository (auto on deploy)

**`_redirects`** (Pages):

```
https://www.seowithfaiz.com/* https://seowithfaiz.com/:splat 301
```

## In Cloudflare Dashboard

### Always Use HTTPS

**SSL/TLS → Edge Certificates → Always Use HTTPS** = On.

### Optional: strip `index.html`

**Rules → Redirect Rules**

| If | URI Path ends with `/index.html` |
| Then | 301 to path without `index.html` |

### Legacy GitHub Pages URLs

`https://fngk.github.io/Mohd-Faizuddin-Ahmed/*` is **not** in your Cloudflare zone. The repo still ships `assets/js/canonical-redirect.js` for browser redirects from old indexed links. Prefer **Search Console** with `seowithfaiz.com` as the primary property.

## DNS (Cloudflare Pages — not GitHub Pages)

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| CNAME | `@` | `your-project.pages.dev` | Proxied |
| CNAME | `www` | `your-project.pages.dev` | Proxied |

Remove `fngk.github.io` CNAMEs when fully migrated.

## Verify

```bash
curl -I "https://www.seowithfaiz.com/"
curl -I "https://seowithfaiz.com/contact/index.html"
```

www should return **301** to apex. Contact form should POST to `/api/v1/contact` on the same host.
