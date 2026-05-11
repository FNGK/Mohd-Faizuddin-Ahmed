#!/usr/bin/env python3
"""Score drafts for humanization and originality; notify when ready to publish."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from draft_io import load_draft, save_draft
from email_notifier import maybe_notify_ready_draft
from humanization import evaluate_draft


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify blog drafts for humanized copy.")
    parser.add_argument("--drafts-dir", default="blog/drafts", help="Draft folder path")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--min-score", type=int, default=72, help="Minimum humanization score")
    parser.add_argument("--min-originality", type=int, default=62, help="Minimum originality score")
    parser.add_argument("--notify", action="store_true", help="Send ready-for-review alerts")
    return parser.parse_args()


def process_draft(
    path: Path,
    repo_root: Path,
    *,
    min_score: int,
    min_originality: int,
    notify: bool,
) -> str:
    meta, body = load_draft(path)
    report = evaluate_draft(
        body,
        str(meta.get("primary_keyword", "")),
        repo_root,
        path,
        min_score=min_score,
        min_originality=min_originality,
    )
    meta.update(report.to_frontmatter())
    meta["last_humanization_check"] = datetime.now(timezone.utc).isoformat()
    meta["review_status"] = "ready" if report.verified else "needs_revision"
    if meta.get("approved") is not True:
        meta["approved"] = False

    notification_detail = ""
    if notify and report.verified:
        sent, notification_detail = maybe_notify_ready_draft(meta)
        if sent or "already notified" in notification_detail:
            meta["ready_notification_sent"] = True
            meta["ready_notification_at"] = datetime.now(timezone.utc).isoformat()

    save_draft(path, meta, body)
    status = "verified" if report.verified else "failed"
    extra = f" | notify: {notification_detail}" if notification_detail else ""
    return f"{path.name}: {status} (score {report.score}, originality {report.originality_score}){extra}"


def main() -> None:
    args = parse_args()
    drafts_dir = Path(args.drafts_dir)
    repo_root = Path(args.repo_root).resolve()
    if not drafts_dir.exists():
        print("No drafts directory found.")
        return

    paths = sorted(p for p in drafts_dir.glob("*.md") if p.name.lower() != "readme.md")
    if not paths:
        print("No drafts to verify.")
        return

    for path in paths:
        print(
            process_draft(
                path,
                repo_root,
                min_score=args.min_score,
                min_originality=args.min_originality,
                notify=args.notify,
            )
        )


if __name__ == "__main__":
    main()
