#!/usr/bin/env python3
"""Local review console with one-click publish for verified drafts."""

from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

from draft_io import load_draft, save_draft
from email_notifier import load_notifier_config
from publish_validator import process_draft as publish_process_draft


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


class ReviewHandler(BaseHTTPRequestHandler):
    drafts_dir = Path("blog/drafts")
    posts_dir = Path("blog/posts")
    template_path = Path("blog/templates/post-template.html")
    index_path = Path("blog/index.html")
    review_html_path = Path("automation/blog/admin/review.html")

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, status: int, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _list_drafts(self) -> list[dict]:
        rows: list[dict] = []
        if not self.drafts_dir.exists():
            return rows
        for path in sorted(self.drafts_dir.glob("*.md")):
            if path.name.lower() == "readme.md":
                continue
            meta, _ = load_draft(path)
            slug = str(meta.get("slug", path.stem))
            rows.append(
                {
                    "slug": slug,
                    "title": meta.get("title", slug),
                    "review_status": meta.get("review_status", "pending"),
                    "humanization_verified": meta.get("humanization_verified") is True,
                    "humanization_score": meta.get("humanization_score"),
                    "originality_score": meta.get("originality_score"),
                    "approved": meta.get("approved") is True,
                    "published": (self.posts_dir / f"{slug}.html").exists(),
                }
            )
        return rows

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/review"}:
            html = self.review_html_path.read_text(encoding="utf-8")
            self._send_html(200, html)
            return
        if parsed.path == "/api/drafts":
            self._send_json(200, {"drafts": self._list_drafts()})
            return
        self._send_json(404, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/api/publish":
            self._send_json(404, {"error": "Not found"})
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        try:
            payload = json.loads(raw or "{}")
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON body"})
            return

        slug = str(payload.get("slug", "")).strip()
        token = str(payload.get("token", "")).strip()
        expected = str(load_notifier_config().get("publish_token", "")).strip()
        if not expected or token != expected:
            self._send_json(403, {"error": "Invalid publish token"})
            return
        if not slug:
            self._send_json(400, {"error": "Missing slug"})
            return

        draft_path = self.drafts_dir / f"{slug}.md"
        if not draft_path.exists():
            self._send_json(404, {"error": f"Draft not found: {slug}"})
            return

        meta, body = load_draft(draft_path)
        if meta.get("humanization_verified") is not True:
            self._send_json(409, {"error": "Draft has not passed humanization verification"})
            return

        meta["approved"] = True
        save_draft(draft_path, meta, body)

        template_text = self.template_path.read_text(encoding="utf-8")
        ok, message = publish_process_draft(
            draft_path,
            template_text,
            self.posts_dir,
            self.index_path,
            publish=True,
        )
        if not ok:
            self._send_json(400, {"error": message})
            return
        self._send_json(200, {"message": message, "slug": slug})

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        sys.stdout.write("%s - %s\n" % (self.address_string(), format % args))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the blog review console.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", type=int, default=8765, help="Bind port")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = repo_root()
    ReviewHandler.drafts_dir = root / "blog" / "drafts"
    ReviewHandler.posts_dir = root / "blog" / "posts"
    ReviewHandler.template_path = root / "blog" / "templates" / "post-template.html"
    ReviewHandler.index_path = root / "blog" / "index.html"
    ReviewHandler.review_html_path = root / "automation" / "blog" / "admin" / "review.html"

    server = ThreadingHTTPServer((args.host, args.port), ReviewHandler)
    print(f"Review console running at http://{args.host}:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping review console.")


if __name__ == "__main__":
    main()
