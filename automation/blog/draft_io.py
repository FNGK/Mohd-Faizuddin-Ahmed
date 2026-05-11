"""Read and write blog draft markdown with YAML frontmatter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def split_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    if not content.startswith("---\n"):
        raise ValueError("Draft missing frontmatter header")
    _, rest = content.split("---\n", 1)
    frontmatter_raw, body = rest.split("\n---\n", 1)
    data = yaml.safe_load(frontmatter_raw) or {}
    return data, body.strip()


def dump_frontmatter(data: dict[str, Any], body: str) -> str:
    header = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{header}\n---\n\n{body.strip()}\n"


def load_draft(path: Path) -> tuple[dict[str, Any], str]:
    return split_frontmatter(path.read_text(encoding="utf-8"))


def save_draft(path: Path, data: dict[str, Any], body: str) -> None:
    path.write_text(dump_frontmatter(data, body), encoding="utf-8")
