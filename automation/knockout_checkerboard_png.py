"""Convert checkerboard-style preview PNGs to real RGBA (SEO logo exports often bake the grid)."""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def knockout_checker(r: int, g: int, b: int) -> bool:
    """Pixels matching light checker squares → transparent."""
    if abs(r - 205) <= 14 and abs(g - 205) <= 14 and abs(b - 205) <= 14:
        return True
    if r >= 248 and g >= 248 and b >= 248:
        return True
    return False


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "assets" / "logos" / "seo-with-faiz-logo-technical-precision-revenue-growth.png"
    im = Image.open(path).convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if knockout_checker(r, g, b):
                px[x, y] = (r, g, b, 0)
    im.save(path, "PNG", optimize=True)
    print(f"Wrote RGBA {path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
