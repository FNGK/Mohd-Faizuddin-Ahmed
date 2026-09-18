"""Remove the Google Fonts tags from every served page (idempotent).

The brand fonts (Fraunces, Hanken Grotesk, JetBrains Mono) are self-hosted from
assets/fonts/ and declared at the top of assets/css/site.css. From 2026-05-17
until 2026-09-18 the Google Fonts request never worked: the Fraunces URL listed
weights without the optical-size value each tuple needs (Google answered 400),
and the stylesheet was switched on by an inline onload handler that the site's
CSP blocks. Self-hosting fixes both, drops a third-party connection, and keeps
visitor IPs away from Google (an EU privacy concern with Google-hosted fonts).

Usage: python automation/self_host_fonts.py [--check]
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", "cms", "automation", ".wrangler"}

# Each pattern removes the whole line it sits on, indentation included.
PATTERNS = [
    re.compile(r'^[ \t]*<link rel="preconnect" href="https://fonts\.googleapis\.com">[ \t]*\r?\n', re.M),
    re.compile(r'^[ \t]*<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>[ \t]*\r?\n', re.M),
    re.compile(r'^[ \t]*<link rel="preload" as="style" href="https://fonts\.googleapis\.com/css2\?[^"]*"[^>]*>[ \t]*\r?\n', re.M),
    re.compile(r'^[ \t]*<noscript><link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]*"></noscript>[ \t]*\r?\n', re.M),
]


def served_pages():
    for path in ROOT.rglob("*.html"):
        if not SKIP_DIRS.intersection(path.relative_to(ROOT).parts):
            yield path


def main():
    check = "--check" in sys.argv
    changed = leftovers = 0
    for page in served_pages():
        text = page.read_text(encoding="utf-8")
        new = text
        for pattern in PATTERNS:
            new = pattern.sub("", new)
        if "fonts.googleapis.com" in new or "fonts.gstatic.com" in new:
            leftovers += 1
            print("still references Google Fonts:", page.relative_to(ROOT))
        if new != text:
            changed += 1
            if not check:
                page.write_text(new, encoding="utf-8", newline="")
    verb = "would change" if check else "changed"
    print(f"{verb} {changed} pages; {leftovers} with Google Fonts references left")
    return 1 if leftovers else 0


if __name__ == "__main__":
    sys.exit(main())
