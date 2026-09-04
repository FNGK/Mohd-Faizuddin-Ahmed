#!/usr/bin/env python3
"""Rebuild assets/css/app.min.css from source (site.css + components.css).

Every page links ONE stylesheet, app.min.css. Edit site.css / components.css,
then run this to regenerate the served bundle:

    python automation/build_css.py

Safe, conservative "minify": strips /* */ comments, drops blank lines, and
trims per-line indentation. It deliberately does NOT collapse whitespace INSIDE
declarations, because values like `color-mix(in srgb, var(--primary) 12%, ...)`
rely on those inner spaces. Order is site.css first (tokens/base), then
components.css (components) — the same order the cascade expects.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "assets" / "css"
SOURCES = ["site.css", "components.css"]


def strip(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)   # remove comments
    lines = (ln.strip() for ln in text.splitlines())     # de-indent
    return "\n".join(ln for ln in lines if ln)           # drop blank lines


def main() -> None:
    out = "\n".join(strip((CSS / name).read_text(encoding="utf-8")) for name in SOURCES) + "\n"
    (CSS / "app.min.css").write_text(out, encoding="utf-8")
    print(f"app.min.css rebuilt: {len(out) // 1024}KB from {', '.join(SOURCES)}")


if __name__ == "__main__":
    main()
