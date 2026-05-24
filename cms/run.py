#!/usr/bin/env python3
"""Run the unified site + CMS API (Hostinger VPS / local dev)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import uvicorn

CMS_DIR = Path(__file__).resolve().parent
BACKEND = CMS_DIR / "backend"
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(CMS_DIR))

from port_util import free_port, pids_on_port  # noqa: E402

PORT = int(os.environ.get("CMS_PORT", "8780"))
HOST = os.environ.get("CMS_HOST", "127.0.0.1")
RELOAD_ENV = os.environ.get("CMS_RELOAD")
# Uvicorn reload on Windows often leaves zombie listeners; default off unless CMS_RELOAD=1.
RELOAD = (
    RELOAD_ENV.lower() in ("1", "true", "yes")
    if RELOAD_ENV is not None
    else sys.platform != "win32"
)


def _prepare_port() -> None:
    if os.environ.get("CMS_FREE_PORT", "1") == "0":
        return
    killed = free_port(PORT)
    if killed:
        print(f"Freed port {PORT} (stopped PIDs: {killed})")
    remaining = [p for p in pids_on_port(PORT) if p != os.getpid()]
    if remaining:
        print(
            f"ERROR: port {PORT} is still in use by PID(s) {remaining}.\n"
            f"Run: powershell -File cms/scripts/stop.ps1",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    _prepare_port()
    kwargs: dict = {
        "app": "app.main:app",
        "host": HOST,
        "port": PORT,
        "reload": RELOAD,
    }
    if RELOAD:
        kwargs["reload_dirs"] = [str(BACKEND), str(CMS_DIR / "admin")]
    print(f"CMS at http://{HOST}:{PORT}/admin/  (reload={'on' if RELOAD else 'off'})")
    uvicorn.run(**kwargs)
