"""Remove baked navy plate from dark-mode logo PNG (opaque RGBA → real transparency)."""
from __future__ import annotations

import math
import sys
from collections import deque
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def _dist(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def flood_knockout(
    im: Image.Image,
    *,
    seeds: list[tuple[int, int]],
    ref: tuple[int, int, int],
    tol: float = 24.0,
) -> Image.Image:
    """Set alpha=0 for background-colored pixels connected from seeds."""
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    seen: set[tuple[int, int]] = set()
    q: deque[tuple[int, int]] = deque()

    def matches(xy: tuple[int, int]) -> bool:
        r, g, b = px[xy[0], xy[1]][:3]
        return _dist((r, g, b), ref) <= tol

    for sx, sy in seeds:
        if matches((sx, sy)):
            q.append((sx, sy))
            seen.add((sx, sy))

    while q:
        x, y = q.popleft()
        r, g, b, _ = px[x, y]
        if _dist((r, g, b), ref) > tol:
            continue
        px[x, y] = (r, g, b, 0)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in seen:
                continue
            seen.add((nx, ny))
            nr, ng, nb = px[nx, ny][:3]
            if _dist((nr, ng, nb), ref) <= tol:
                q.append((nx, ny))

    return im


def main() -> None:
    rel = sys.argv[1] if len(sys.argv) > 1 else "assets/logos/seo-with-faiz-logo-dark-mode-technical-precision-revenue-growth.png"
    path = ROOT / rel
    im = Image.open(path).convert("RGBA")
    ref = im.getpixel((0, 0))[:3]
    w, h = im.size
    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    out = flood_knockout(im, seeds=seeds, ref=ref, tol=24.0)
    out.save(path, "PNG", optimize=True)
    a = out.split()[3]
    print(f"Wrote {path} alpha={a.getextrema()} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
