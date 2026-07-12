#!/usr/bin/env python3
"""Inject the GTM head loader + body <noscript> into every deployed HTML page.

- Head: <script src="/assets/js/gtm-loader.js" defer></script> before </head>
  (external, CSP-safe; the loader sets Consent Mode defaults then loads GTM).
- Body: the standard GTM <noscript> iframe right after <body ...>.

Idempotent (skips files that already contain GTM-KQ9KNHN2). Skips the dirs
wrangler excludes from deploy. Preserves CRLF line endings.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = "GTM-KQ9KNHN2"
HEAD_TAG = '  <script src="/assets/js/gtm-loader.js" defer></script>\n</head>'
NOSCRIPT = (
    '\n  <!-- Google Tag Manager (noscript) -->\n'
    '  <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-KQ9KNHN2"\n'
    '  height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>\n'
    '  <!-- End Google Tag Manager (noscript) -->'
)

# Directories excluded from the deployed site (mirror wrangler.jsonc) + app dirs.
SKIP_DIRS = {
    ".git", ".wrangler", "node_modules", "cms", "server", "automation",
    "client-acquisition-engine", "functions", "seowithfaiz-app", "auto-dm-setup",
}
SKIP_FILES = {"Professional_Resume.html", "formsubmit-test-out.html"}

body_re = re.compile(r"(<body[^>]*>)", re.IGNORECASE)


def deployed_html():
    for p in ROOT.rglob("*.html"):
        rel = p.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if p.name in SKIP_FILES:
            continue
        yield p


def main():
    changed, skipped, missing = [], [], []
    for p in deployed_html():
        text = p.read_text(encoding="utf-8")
        if MARKER in text:
            skipped.append(p)
            continue
        if "</head>" not in text or not body_re.search(text):
            missing.append(p)
            continue
        text = text.replace("</head>", HEAD_TAG, 1)
        text = body_re.sub(lambda m: m.group(1) + NOSCRIPT, text, count=1)
        # Normalize to CRLF to match the repo's Windows line endings.
        p.write_text(text, encoding="utf-8", newline="\r\n")
        changed.append(p)

    print(f"changed: {len(changed)}")
    for p in changed:
        print("  +", p.relative_to(ROOT))
    print(f"skipped (already had GTM): {len(skipped)}")
    if missing:
        print(f"SKIPPED (no </head> or <body>): {len(missing)}")
        for p in missing:
            print("  ?", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
