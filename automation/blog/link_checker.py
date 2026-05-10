#!/usr/bin/env python3
"""Check local relative links inside HTML files."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(".").resolve()
HTML_FILES = [p for p in ROOT.rglob("*.html") if ".git" not in p.parts]
ATTR_PATTERN = re.compile(r'(href|src)="([^"]+)"')
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#", "javascript:", "data:")


def main() -> None:
    broken = []
    for html_file in HTML_FILES:
        text = html_file.read_text(encoding="utf-8", errors="ignore")
        for attr, target in ATTR_PATTERN.findall(text):
            if not target or target.startswith(SKIP_PREFIXES):
                continue
            if "{{" in target and "}}" in target:
                continue
            clean = target.split("?", 1)[0].split("#", 1)[0]
            resolved = (html_file.parent / clean).resolve()
            if not resolved.exists():
                broken.append((html_file.relative_to(ROOT), attr, target))

    if not broken:
        print("No broken local links found.")
        return

    print(f"Broken local links: {len(broken)}")
    for file_path, attr, target in broken:
        print(f"{file_path} | {attr} -> {target}")


if __name__ == "__main__":
    main()
