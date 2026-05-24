#!/usr/bin/env python3
"""Inject canonical-redirect.js into public HTML <head> blocks."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {"cms", "automation"}
SKIP_NAMES = {"formsubmit-test-out.html", "Professional_Resume.html"}
MARKER = "canonical-redirect.js"
SNIPPET_TMPL = '  <script src="{prefix}assets/js/canonical-redirect.js"></script>\n'


def prefix_for(path: Path) -> str:
    depth = len(path.relative_to(ROOT).parts) - 1
    return "../" * depth if depth else "./"


def main() -> None:
    count = 0
    for html in ROOT.rglob("*.html"):
        rel = html.relative_to(ROOT)
        if any(part in SKIP_PARTS for part in rel.parts) or rel.name in SKIP_NAMES:
            continue
        text = html.read_text(encoding="utf-8")
        if MARKER in text:
            continue
        if "<head>" not in text:
            continue
        snippet = SNIPPET_TMPL.format(prefix=prefix_for(html))
        html.write_text(text.replace("<head>", "<head>\n" + snippet, 1), encoding="utf-8")
        print("updated", rel)
        count += 1
    print("total", count)


if __name__ == "__main__":
    main()
