#!/usr/bin/env python3
"""Apply shared page shell: body classes and premium footer."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {
    ROOT / "Professional_Resume.html",
    ROOT / "automation" / "blog" / "admin" / "review.html",
}


def prefix_for(path: Path) -> str:
    depth = len(path.relative_to(ROOT).parts) - 1
    return "./" if depth == 0 else "../" * depth


def footer_html(prefix: str) -> str:
    return f"""  <footer class="site-footer">
    <div class="container site-footer__grid">
      <div class="site-footer__brand">
        <p class="site-footer__title">SEO With Faiz</p>
        <p>Technical SEO, local growth, and answer-engine visibility for companies that need pipeline, not vanity traffic.</p>
        <p><a href="{prefix}contact/index.html">Book a strategy call</a> · <a href="mailto:md.faiz.ahmed62@gmail.com">md.faiz.ahmed62@gmail.com</a></p>
      </div>
      <div>
        <p class="site-footer__title">Services</p>
        <nav class="site-footer__links" aria-label="Footer services">
          <a href="{prefix}services/technical-seo.html">Technical SEO</a>
          <a href="{prefix}services/local-seo.html">Local SEO</a>
          <a href="{prefix}services/international-seo.html">International SEO</a>
          <a href="{prefix}services/content-seo.html">Content SEO</a>
        </nav>
      </div>
      <div>
        <p class="site-footer__title">Proof</p>
        <nav class="site-footer__links" aria-label="Footer proof">
          <a href="{prefix}case-studies/index.html">Case studies</a>
          <a href="{prefix}mentions.html">Mentions</a>
          <a href="{prefix}resources/seo-audit-playbook.html">SEO playbook</a>
          <a href="{prefix}free-tools/gsc-error-priority-calculator.html">GSC calculator</a>
        </nav>
      </div>
      <div>
        <p class="site-footer__title">Company</p>
        <nav class="site-footer__links" aria-label="Footer company">
          <a href="{prefix}about/index.html">About</a>
          <a href="{prefix}blog/index.html">Blog</a>
          <a href="{prefix}contact/index.html">Contact</a>
        </nav>
      </div>
    </div>
    <div class="container site-footer__bottom">
      <span>© <span data-current-year>2026</span> SEO With Faiz · seowithfaiz.com</span>
      <span>USA · Canada · Australia · Europe · India</span>
    </div>
  </footer>"""


def body_class(path: Path) -> str:
    if path.name == "index.html" and path.parent == ROOT:
        return "page-home"
    return "page-inner"


def patch_body_tag(html: str, class_name: str) -> str:
    if re.search(r"<body[^>]*class=", html):
        return re.sub(r'<body[^>]*class="[^"]*"', f'<body class="{class_name}"', html, count=1)
    return re.sub(r"<body>", f'<body class="{class_name}">', html, count=1)


def main() -> None:
    changed = 0
    for path in ROOT.rglob("*.html"):
        if path in SKIP or "node_modules" in path.parts:
            continue
        original = path.read_text(encoding="utf-8")
        footer = footer_html(prefix_for(path))
        updated = re.sub(r"<footer[\s\S]*?</footer>", footer, patch_body_tag(original, body_class(path)), count=1)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print(f"shell {path.relative_to(ROOT)}")
    print(f"Shell applied to {changed} files.")


if __name__ == "__main__":
    main()
