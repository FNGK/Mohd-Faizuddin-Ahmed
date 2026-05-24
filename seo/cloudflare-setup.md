# Cloudflare setup — seowithfaiz.com (production)

Hosting is **Cloudflare Pages** (static site + Pages Functions for the contact API). Email uses **Cloudflare Email Routing** (`win@seowithfaiz.com` → your Gmail inbox).

## 1. Pages project

| Setting | Value |
|---------|--------|
| **Production branch** | `main` |
| **Build command** | *(leave empty — static HTML repo)* |
| **Build output directory** | `/` (repository root) |
| **Custom domains** | `seowithfaiz.com`, `www.seowithfaiz.com` |

After each push to `main`, Pages redeploys automatically.

## 2. DNS (if not already)

In **Cloudflare → seowithfaiz.com → DNS**:

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| CNAME | `@` | `<your-pages-subdomain>.pages.dev` | Proxied |
| CNAME | `www` | `<your-pages-subdomain>.pages.dev` | Proxied |

Remove old `CNAME` records pointing at `fngk.github.io` if you have fully left GitHub Pages.

**Pages custom domain:** Dashboard → Workers & Pages → your project → **Custom domains** → add `seowithfaiz.com` and `www.seowithfaiz.com`.

## 3. Redirects (in repo + dashboard)

- **Repo:** `_redirects` — `www` → apex (301).
- **Dashboard:** SSL/TLS → **Always Use HTTPS** = On.
- Optional Redirect Rule for `/index.html` → `/` (see `seo/cloudflare-redirects.md`).

## 4. Security headers

- **Repo:** `_headers` (applied by Cloudflare Pages on deploy).
- Verify: `curl -I https://seowithfaiz.com/` shows `content-security-policy`, `strict-transport-security`.

## 5. Email Routing (official address)

**Email → Email Routing → Routing rules**

| Custom address | Action | Destination |
|----------------|--------|-------------|
| `win@seowithfaiz.com` | Send to | `win@seowithfaiz.com` |

Also enable:

- **win@seowithfaiz.com** as allowed sender for Mailchannels (domain on Cloudflare; SPF/DKIM auto for routing).
- Optional: `admin@seowithfaiz.com` → same inbox (CMS admin).

## 6. Contact form API (Pages Functions + secrets)

The form posts to `https://seowithfaiz.com/api/v1/contact`, implemented in `functions/api/v1/contact.js` (Mailchannels).

**Workers & Pages → your project → Settings → Environment variables** (Production):

| Variable | Example | Required |
|----------|---------|----------|
| `CONTACT_NOTIFY_TO` | `md.faiz.ahmed62@gmail.com` | Yes — inbox where inquiries land |
| `CONTACT_FROM_EMAIL` | `win@seowithfaiz.com` | Yes — From address (must be on your zone) |
| `CONTACT_FROM_NAME` | `SEO With Faiz` | Optional |

No API keys needed for Mailchannels when sending from a Cloudflare-proxied domain.

**Test after deploy:**

```bash
curl -X POST "https://seowithfaiz.com/api/v1/contact" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test\",\"email\":\"you@company.com\",\"website\":\"https://example.com\",\"region\":\"USA\",\"goal\":\"Testing contact API after Cloudflare deploy.\",\"honeypot\":\"\"}"
```

Expect `201` and an email in Gmail.

## 7. GitHub Pages / old URLs

Indexed `fngk.github.io/Mohd-Faizuddin-Ahmed/*` URLs still use in-repo `canonical-redirect.js` (client redirect). Prefer **Google Search Console** → property `seowithfaiz.com` → remove old GH property over time.

## 8. Automations (GitHub Actions — optional)

Blog draft workflow (`.github/workflows/blog-draft-generator.yml`) needs **GitHub repository secrets** (not Cloudflare):

| Secret | Purpose |
|--------|---------|
| `BLOG_SMTP_HOST` | e.g. `smtp.gmail.com` or SMTP for `win@seowithfaiz.com` |
| `BLOG_SMTP_PORT` | `587` |
| `BLOG_SMTP_USER` | SMTP login |
| `BLOG_SMTP_PASSWORD` | App password |
| `BLOG_NOTIFY_FROM` | `win@seowithfaiz.com` |
| `BLOG_REVIEW_BASE_URL` | `https://seowithfaiz.com` (or review app URL) |

`BLOG_NOTIFY_TO` is set in the workflow file (inbox email).

**Marketing agent** (`automation/marketing_agent/`): set `OPENAI_API_KEY` locally or in CI secrets — not used on the public site.

**CMS** (`cms/`): only if you run the admin API on a VPS later; not required for Cloudflare Pages–only hosting.

## 9. Pre–client-share checklist

- [ ] `https://seowithfaiz.com/` loads with valid SSL
- [ ] `https://www.seowithfaiz.com/` 301 → apex
- [ ] Contact form submits → thank-you page
- [ ] Inquiry email arrives in Gmail
- [ ] Footer / contact page show **win@seowithfaiz.com**
- [ ] No links to `formsubmit.co`
- [ ] Lighthouse / mobile check on home + contact

## 10. Troubleshooting

| Issue | Fix |
|-------|-----|
| Form API 404 | Redeploy Pages; confirm `functions/api/v1/contact.js` is on `main` |
| Form 503 / email not sent | Check Pages env vars; confirm domain uses Cloudflare DNS; check Mailchannels in Workers logs |
| CSP blocks fonts | `_headers` includes `fonts.googleapis.com` / `gstatic.com` |
| Old FormSubmit | Hard refresh; confirm latest `contact/index.html` deployed |
