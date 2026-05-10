#!/usr/bin/env python3
"""Point header markup at SEO-named transparent dark logo."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OLD = "seowithfaiz-logo-lockup-dark.png"
NEW = "seo-with-faiz-logo-dark-mode-technical-precision-revenue-growth.png"
OLD_DIM = 'width="320" height="72"'
NEW_DIM = 'width="580" height="228"'


def main() -> None:
    exts = {".html", ".py", ".txt", ".md"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in exts:
            continue
        if path.name == "update_dark_logo_asset.py":
            continue
        text = path.read_text(encoding="utf-8")
        new = text.replace(OLD, NEW)
        out_lines = []
        for line in new.splitlines():
            if "brand-logo--dark" in line and OLD_DIM in line:
                line = line.replace(OLD_DIM, NEW_DIM)
            out_lines.append(line)
        new = "\n".join(out_lines) + ("\n" if text.endswith("\n") else "")
        if new != text:
            path.write_text(new, encoding="utf-8")
            print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
