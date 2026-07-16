#!/usr/bin/env python3
"""Branded Instagram/social card generator for SEO With Faiz.

Renders a 1080x1080 dark-premium card matching the site's identity:
navy gradient, dot grid, teal accent, Fraunces statement, Hanken support.

Usage:
  python automation/social/make_card.py \
      --statement "The trick isn't the 3D. It's when it loads." \
      --support "Craft notes from the studio" \
      --out assets/social/2026-07-07-3d-loading.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FONTS = Path(__file__).resolve().parent / "fonts"

W = H = 1080
NAVY_TOP = (6, 14, 27)      # #060e1b
NAVY_MID = (10, 33, 42)     # teal-tinted midpoint
NAVY_BOT = (8, 20, 40)      # #081428
TEAL = (47, 212, 198)       # #2fd4c6
INK_TEXT = (232, 251, 248)  # #e8fbf8
MUTED = (170, 195, 205)


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient_bg():
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        t = y / (H - 1)
        c = lerp(NAVY_TOP, NAVY_MID, t / 0.55) if t < 0.55 else lerp(NAVY_MID, NAVY_BOT, (t - 0.55) / 0.45)
        for x in range(W):
            px[x, y] = c
    return im


def dot_grid(draw):
    for y in range(40, H, 44):
        for x in range(40, W, 44):
            draw.ellipse([x, y, x + 2, y + 2], fill=(255, 255, 255, 14))


def font(path, size, variation=None):
    f = ImageFont.truetype(str(path), size)
    if variation:
        try:
            f.set_variation_by_axes(variation)
        except Exception:
            pass
    return f


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render(statement: str, support: str, out: Path):
    base = gradient_bg().convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    dot_grid(d)

    # teal glow, top-right
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W - 460, -260, W + 260, 460], fill=(47, 212, 198, 46))
    from PIL import ImageFilter
    glow = glow.filter(ImageFilter.GaussianBlur(140))
    base = Image.alpha_composite(base, glow)
    base = Image.alpha_composite(base, overlay)
    d = ImageDraw.Draw(base)

    margin = 96
    # kicker: accent dash + support label (top)
    # size adapts like the statement below: shrink until it fits in 2 lines
    kick_w = W - margin - (margin + 76)
    kick_size = 34
    while kick_size > 20:
        kick_f = font(FONTS / "HankenGrotesk.ttf", kick_size, [700])
        kick_lines = wrap(d, support.upper(), kick_f, kick_w)
        if len(kick_lines) <= 2:
            break
        kick_size -= 2
    d.rounded_rectangle([margin, margin + 8, margin + 56, margin + 14], 3, fill=TEAL)
    kick_line_h = int(kick_size * 1.3)
    ky = margin - 8
    for kl in kick_lines:
        d.text((margin + 76, ky), kl, font=kick_f, fill=TEAL)
        ky += kick_line_h

    # statement (Fraunces, semibold, generous leading)
    # size adapts: shrink until it fits in 6 lines
    size = 92
    while size > 54:
        st_f = font(FONTS / "Fraunces.ttf", size, [72, 600, 0, 1])
        lines = wrap(d, statement, st_f, W - margin * 2)
        line_h = int(size * 1.18)
        if len(lines) * line_h <= 620:
            break
        size -= 6
    total_h = len(lines) * line_h
    y = (H - total_h) // 2 + 10
    for ln in lines:
        d.text((margin, y), ln, font=st_f, fill=INK_TEXT)
        y += line_h

    # bottom bar: brand + site
    brand_f = font(FONTS / "HankenGrotesk.ttf", 40, [800])
    site_f = font(FONTS / "HankenGrotesk.ttf", 34, [600])
    d.text((margin, H - margin - 44), "SEO With Faiz", font=brand_f, fill=INK_TEXT)
    site_txt = "seowithfaiz.com"
    stw = d.textlength(site_txt, font=site_f)
    d.text((W - margin - stw, H - margin - 40), site_txt, font=site_f, fill=MUTED)
    # thin divider above bottom bar
    d.line([margin, H - margin - 78, W - margin, H - margin - 78],
           fill=(255, 255, 255, 36), width=2)

    out.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(out, "PNG", optimize=True)
    print(f"card written: {out} ({out.stat().st_size // 1024}KB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--statement", required=True)
    ap.add_argument("--support", default="From the studio")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    render(a.statement, a.support, ROOT / a.out if not Path(a.out).is_absolute() else Path(a.out))


if __name__ == "__main__":
    main()
