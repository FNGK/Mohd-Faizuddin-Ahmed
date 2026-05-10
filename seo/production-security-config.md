# Production Security and Performance Controls

These controls are host-level and cannot be enforced by HTML alone.

## Required Security Headers

Use these headers on all HTML responses:

- `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`
- `Content-Security-Policy: default-src 'self'; img-src 'self' data: https:; script-src 'self' https://www.googletagmanager.com; style-src 'self' 'unsafe-inline'; connect-src 'self' https://www.google-analytics.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self' https://formsubmit.co`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), camera=(), microphone=()`

## HSTS and HTTPS

- Force HTTP to HTTPS with 301 redirects.
- Enable HSTS only after HTTPS is stable on all subdomains.
- Submit for preload only after verifying no mixed-content dependencies.

## HTTP/3

- Enable QUIC/HTTP3 at CDN or hosting edge (Cloudflare, Fastly, or provider settings).
- Verify with browser devtools protocol column and online validators.

## Performance Controls

- Use Brotli compression on text assets.
- Set long cache headers for versioned static assets.
- Keep third-party scripts minimal (GA only by default).
- Use image width/height attributes to avoid CLS.

## Hosting Checklist

1. Enable TLS certificate for `seowithfaiz.com`.
2. Enable HTTP/3 in hosting/CDN control panel.
3. Configure response headers from this file.
4. Run Core Web Vitals tests on mobile and desktop after cutover.
