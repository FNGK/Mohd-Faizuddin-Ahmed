#!/usr/bin/env python3
"""Dynamic social image for SEO With Faiz — real-world creative, light signature.

Takes a full-bleed, topic-matched image (Canva AI `generate-image` or free
stock from `asset_search`) and stamps a small, consistent brand signature in
the corner (logo mark + wordmark + @handle) over a subtle scrim so it reads on
ANY image — dark or light. The post's message lives in the CAPTION, not on the
image. This REPLACES the single navy card for Instagram.

Usage:
  python automation/social/make_social_image.py \
      --image /tmp/canva-hero.jpg \
      --out assets/social/2026-10-13-page-speed.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FONTS = Path(__file__).resolve().parent / "fonts"
LOGO = ROOT / "assets" / "social" / "brand" / "icon-mark.png"

W = H = 1080
INK = (245, 250, 252)
MUTED = (196, 210, 220)
TEAL = (47, 212, 198)
NAVY = (6, 14, 27)


def font(path, size, variation=None):
    f = ImageFont.truetype(str(path), size)
    if variation:
        try:
            f.set_variation_by_axes(variation)
        except Exception:
            pass
    return f


def cover_resize(img, w, h):
    sw, sh = img.size
    scale = max(w / sw, h / sh)
    nw, nh = round(sw * scale), round(sh * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return img.crop((left, top, left + w, top + h))


def bottom_scrim(base, strength=150, frac=0.30):
    """Soft navy gradient on the bottom band so the signature always reads."""
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gp = grad.load()
    start = int(H * (1 - frac))
    for y in range(start, H):
        t = (y - start) / (H - start)
        a = int(strength * (t ** 1.4))
        row = (*NAVY, a)
        for x in range(W):
            gp[x, y] = row
    return Image.alpha_composite(base, grad)


def signature(base, handle="@seo_with_faiz"):
    d = ImageDraw.Draw(base)
    pad = 56
    icon_sz = 58
    ix, iy = pad, H - pad - icon_sz
    tx = ix + icon_sz + 18
    # logo mark (fallback: a small teal hexagon)
    if LOGO.exists():
        logo = Image.open(LOGO).convert("RGBA").resize((icon_sz, icon_sz), Image.LANCZOS)
        base.paste(logo, (ix, iy), logo)
    else:
        cx, cy, r = ix + icon_sz / 2, iy + icon_sz / 2, icon_sz / 2
        import math
        pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
               for a in range(-90, 270, 60)]
        d.polygon(pts, outline=TEAL, width=3)
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=TEAL)
    d = ImageDraw.Draw(base)
    d.text((tx, iy + 2), "SEO With Faiz", font=font(FONTS / "HankenGrotesk.ttf", 30, [800]), fill=INK)
    d.text((tx, iy + 34), handle, font=font(FONTS / "HankenGrotesk.ttf", 21, [600]), fill=MUTED)
    return base


def render(image: Path, out: Path, handle: str = "@seo_with_faiz"):
    base = cover_resize(Image.open(image).convert("RGBA"), W, H)
    base = bottom_scrim(base)
    base = signature(base, handle)
    out.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(out, "PNG", optimize=True)
    print(f"social image written: {out} ({out.stat().st_size // 1024}KB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True, help="Full-bleed source image (AI or stock).")
    ap.add_argument("--out", required=True)
    ap.add_argument("--handle", default="@seo_with_faiz")
    a = ap.parse_args()
    img = Path(a.image) if Path(a.image).is_absolute() else ROOT / a.image
    out = Path(a.out) if Path(a.out).is_absolute() else ROOT / a.out
    render(img, out, a.handle)


if __name__ == "__main__":
    main()
