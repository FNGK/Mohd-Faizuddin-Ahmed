#!/usr/bin/env python3
"""Point site metadata and automation defaults to https://seowithfaiz.com."""

from __future__ import annotations

from pathlib import Path

OLD = "https://seowithfaiz.com"
NEW = "https://seowithfaiz.com"
OLD_HOST = "seowithfaiz.com"
NEW_HOST = "seowithfaiz.com"

ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {".html", ".md", ".xml", ".txt", ".py", ".gs", ".csv", ".json", ".yml", ".yaml"}


def should_scan(path: Path) -> bool:
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return False
    parts = set(path.parts)
    if "node_modules" in parts or "__pycache__" in parts:
        return False
    return True


def migrate_text(text: str) -> str:
    return text.replace(OLD, NEW).replace(OLD_HOST, NEW_HOST)


def main() -> None:
    changed = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or not should_scan(path):
            continue
        original = path.read_text(encoding="utf-8")
        updated = migrate_text(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print(f"updated {path.relative_to(ROOT)}")
    print(f"Domain migration complete. Files changed: {changed}")


if __name__ == "__main__":
    main()
