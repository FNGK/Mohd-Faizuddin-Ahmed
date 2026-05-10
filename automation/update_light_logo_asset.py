#!/usr/bin/env python3
"""Point header + pipeline files at SEO-named transparent light logo."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OLD = "seowithfaiz-logo-lockup-light.png"
NEW = "seo-with-faiz-logo-technical-precision-revenue-growth.png"
ALT_OLD = 'alt="SEO With Faiz — Technical Precision. Revenue Growth."'
ALT_NEW = (
    'alt="SEO With Faiz logo — technical SEO and revenue growth services; '
    'shield mark with code, bridge, and growth chart (transparent PNG for light mode)."'
)

OLD_DIM = 'width="320" height="72"'
NEW_DIM = 'width="1024" height="498"'


def main() -> None:
    exts = {".html", ".py", ".txt", ".md"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in exts:
            continue
        if path.name == "update_light_logo_asset.py":
            continue
        text = path.read_text(encoding="utf-8")
        new = text.replace(OLD, NEW).replace(ALT_OLD, ALT_NEW)
        out_lines = []
        for line in new.splitlines():
            if "brand-logo--light" in line and OLD_DIM in line:
                line = line.replace(OLD_DIM, NEW_DIM)
            out_lines.append(line)
        new = "\n".join(out_lines) + ("\n" if text.endswith("\n") else "")
        if new != text:
            path.write_text(new, encoding="utf-8")
            print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
