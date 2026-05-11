#!/usr/bin/env python3
"""Run trend collection through humanization verification."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(command: list[str]) -> None:
    print(f"+ {' '.join(command)}")
    subprocess.run(command, check=True)


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    py = sys.executable
    blog_dir = root / "automation" / "blog"
    run([py, str(blog_dir / "trend_collector.py")])
    run([py, str(blog_dir / "keyword_planner.py")])
    run([py, str(blog_dir / "draft_generator.py")])
    run([py, str(blog_dir / "humanization_gate.py"), "--notify"])
    run([py, str(blog_dir / "publish_validator.py")])


if __name__ == "__main__":
    main()
