"""Port helpers for CMS dev server (Windows-friendly)."""

from __future__ import annotations

import os
import subprocess
import sys


def pids_on_port(port: int) -> list[int]:
    """Return process IDs listening on TCP *port* (best-effort)."""
    if sys.platform == "win32":
        try:
            out = subprocess.check_output(
                ["netstat", "-ano"],
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except (OSError, subprocess.CalledProcessError):
            return []
        needle = f":{port}"
        pids: set[int] = set()
        for line in out.splitlines():
            if "LISTENING" not in line or needle not in line:
                continue
            parts = line.split()
            if not parts:
                continue
            try:
                pids.add(int(parts[-1]))
            except ValueError:
                continue
        return sorted(pids)

    try:
        out = subprocess.check_output(
            ["lsof", "-ti", f":{port}"],
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    return sorted({int(x) for x in out.split() if x.strip().isdigit()})


def free_port(port: int) -> list[int]:
    """Terminate processes listening on *port*. Returns PIDs killed."""
    killed: list[int] = []
    for pid in pids_on_port(port):
        if pid == os.getpid():
            continue
        try:
            if sys.platform == "win32":
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(pid)],
                    check=False,
                    capture_output=True,
                )
            else:
                os.kill(pid, 9)
            killed.append(pid)
        except OSError:
            continue
    return killed


def port_in_use(port: int) -> bool:
    return bool(pids_on_port(port))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CMS port utilities")
    parser.add_argument("--free", type=int, metavar="PORT", help="Kill listeners on PORT")
    parser.add_argument("--check", type=int, metavar="PORT", help="Exit 1 if PORT is in use")
    args = parser.parse_args()
    if args.free is not None:
        killed = free_port(args.free)
        print(f"Freed port {args.free}: PIDs {killed or 'none'}")
    elif args.check is not None:
        pids = pids_on_port(args.check)
        if pids:
            print(f"Port {args.check} in use by: {pids}")
            sys.exit(1)
        print(f"Port {args.check} is free")
    else:
        parser.print_help()
