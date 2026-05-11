"""Notify when a blog draft passes humanization and is ready for review."""

from __future__ import annotations

import json
import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any


DEFAULT_NOTIFY_TO = "md.faiz.ahmed62@gmail.com"
ALERTS_PATH = Path("automation/blog/data/ready_alerts.json")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_notifier_config() -> dict[str, Any]:
    root = repo_root()
    config: dict[str, Any] = {
        "notify_to": os.getenv("BLOG_NOTIFY_TO", DEFAULT_NOTIFY_TO),
        "notify_from": os.getenv("BLOG_NOTIFY_FROM", os.getenv("SMTP_USER", "")),
        "smtp_host": os.getenv("SMTP_HOST", ""),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "smtp_user": os.getenv("SMTP_USER", ""),
        "smtp_password": os.getenv("SMTP_PASSWORD", ""),
        "review_base_url": os.getenv("BLOG_REVIEW_BASE_URL", "http://127.0.0.1:8765"),
        "publish_token": os.getenv("BLOG_PUBLISH_TOKEN", ""),
    }
    for name in ("config.local.json", "config.json"):
        path = root / "automation" / "blog" / name
        if path.exists():
            file_data = json.loads(path.read_text(encoding="utf-8"))
            config.update({k: v for k, v in file_data.items() if v not in ("", None)})
    return config


def append_ready_alert(entry: dict[str, Any]) -> None:
    ALERTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing: list[dict[str, Any]] = []
    if ALERTS_PATH.exists():
        existing = json.loads(ALERTS_PATH.read_text(encoding="utf-8"))
    existing.append(entry)
    ALERTS_PATH.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def build_ready_email(draft: dict[str, Any], config: dict[str, Any]) -> EmailMessage:
    slug = draft.get("slug", "unknown-slug")
    title = draft.get("title", slug)
    score = draft.get("humanization_score", "n/a")
    originality = draft.get("originality_score", "n/a")
    review_url = f"{config['review_base_url'].rstrip('/')}/?slug={slug}"

    message = EmailMessage()
    message["Subject"] = f"Blog ready for review: {title}"
    message["From"] = config["notify_from"] or config["smtp_user"] or "blog-automation@local"
    message["To"] = config["notify_to"]
    message.set_content(
        "\n".join(
            [
                "A new blog draft passed humanization checks and is ready for one-click publish.",
                "",
                f"Title: {title}",
                f"Slug: {slug}",
                f"Humanization score: {score}",
                f"Originality score: {originality}",
                "",
                f"Review console: {review_url}",
                "",
                "Open the review console, confirm the draft, then use Publish once to ship the HTML post.",
            ]
        )
    )
    return message


def send_ready_email(draft_meta: dict[str, Any]) -> tuple[bool, str]:
    config = load_notifier_config()
    message = build_ready_email(draft_meta, config)

    host = str(config.get("smtp_host", "")).strip()
    user = str(config.get("smtp_user", "")).strip()
    password = str(config.get("smtp_password", "")).strip()

    if not host or not user or not password:
        append_ready_alert(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "slug": draft_meta.get("slug"),
                "title": draft_meta.get("title"),
                "humanization_score": draft_meta.get("humanization_score"),
                "originality_score": draft_meta.get("originality_score"),
                "delivery": "logged",
                "reason": "SMTP not configured; alert stored locally",
            }
        )
        return False, "SMTP not configured; wrote automation/blog/data/ready_alerts.json"

    message["From"] = config.get("notify_from") or user
    with smtplib.SMTP(host, int(config["smtp_port"])) as server:
        server.starttls(context=ssl.create_default_context())
        server.login(user, password)
        server.send_message(message)
    return True, f"Email sent to {config['notify_to']}"


def maybe_notify_ready_draft(meta: dict[str, Any]) -> tuple[bool, str]:
    if meta.get("humanization_verified") is not True:
        return False, "not verified"
    if meta.get("approved") is True:
        return False, "already approved"
    if meta.get("ready_notification_sent") is True:
        return False, "already notified"
    sent, detail = send_ready_email(meta)
    return sent, detail
