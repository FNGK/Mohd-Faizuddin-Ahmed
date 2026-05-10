#!/usr/bin/env python3
"""Swap single header lockup img for light+dark pair (paths preserved per page)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

WITH_FP = re.compile(
    r'<img class="brand-logo" src="([^"]*?)seowithfaiz-logo-lockup\.png" '
    r'alt="SEO With Faiz — Technical Precision\. Revenue Growth\." '
    r'width="320" height="72" decoding="async" fetchpriority="high">'
)

WITH_FP_REP = (
    r'<img class="brand-logo brand-logo--light" src="\1seo-with-faiz-logo-technical-precision-revenue-growth.png" '
    r'alt="SEO With Faiz logo — technical SEO and revenue growth services; shield mark with code, bridge, and growth chart (transparent PNG for light mode)." '
    r'width="1024" height="498" decoding="async" fetchpriority="high">'
    "\n"
    r'        <img class="brand-logo brand-logo--dark" src="\1seo-with-faiz-logo-dark-mode-technical-precision-revenue-growth.png" '
    r'alt="" width="580" height="228" decoding="async" aria-hidden="true">'
)

STD = re.compile(
    r'<img class="brand-logo" src="([^"]*?)seowithfaiz-logo-lockup\.png" '
    r'alt="SEO With Faiz — Technical Precision\. Revenue Growth\." '
    r'width="320" height="72" decoding="async">'
)

STD_REP = (
    r'<img class="brand-logo brand-logo--light" src="\1seo-with-faiz-logo-technical-precision-revenue-growth.png" '
    r'alt="SEO With Faiz logo — technical SEO and revenue growth services; shield mark with code, bridge, and growth chart (transparent PNG for light mode)." '
    r'width="1024" height="498" decoding="async">'
    "\n"
    r'        <img class="brand-logo brand-logo--dark" src="\1seo-with-faiz-logo-dark-mode-technical-precision-revenue-growth.png" '
    r'alt="" width="580" height="228" decoding="async" aria-hidden="true">'
)


def main() -> None:
    for path in sorted(ROOT.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        new = WITH_FP.sub(WITH_FP_REP, text)
        new = STD.sub(STD_REP, new)
        if new != text:
            path.write_text(new, encoding="utf-8")
            print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
