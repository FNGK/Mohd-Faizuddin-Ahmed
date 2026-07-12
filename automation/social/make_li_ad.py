#!/usr/bin/env python3
"""Branded LinkedIn single-image ad generator for SEO With Faiz.

Renders a 1200x627 (LinkedIn Sponsored Content spec) dark-premium ad matching
the site identity: navy gradient, dot grid, teal accent, Fraunces statement,
Hanken support + CTA chip.

Usage:
  python automation/social/make_li_ad.py \
      --statement "Every direct booking you lose pays an OTA 15-25%." \
      --support "For boutique hotels" \
      --cta "Free 10-minute site teardown" \
      --out assets/social/linkedin-ad-hospitality-teardown.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
FONTS = Path(__file__).resolve().parent / "fonts"

W, H = 1200, 627
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


def render(statement: str, support: str, cta: str, out: Path):
    base = gradient_bg().convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    dot_grid(d)

    # teal glow, right side
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W - 420, -220, W + 260, 500], fill=(47, 212, 198, 42))
    glow = glow.filter(ImageFilter.GaussianBlur(150))
    base = Image.alpha_composite(base, glow)
    base = Image.alpha_composite(base, overlay)
    d = ImageDraw.Draw(base)

    margin = 84
    content_w = W - margin * 2

    # kicker: accent dash + support label (top)
    kick_f = font(FONTS / "HankenGrotesk.ttf", 30, [700])
    d.rounded_rectangle([margin, margin + 6, margin + 52, margin + 12], 3, fill=TEAL)
    d.text((margin + 70, margin - 10), support.upper(), font=kick_f, fill=TEAL)

    # statement (Fraunces, semibold) — shrink to fit up to 4 lines
    size = 78
    while size > 44:
        st_f = font(FONTS / "Fraunces.ttf", size, [72, 600, 0, 1])
        lines = wrap(d, statement, st_f, content_w)
        line_h = int(size * 1.16)
        if len(lines) * line_h <= 300:
            break
        size -= 4
    y = margin + 74
    for ln in lines:
        d.text((margin, y), ln, font=st_f, fill=INK_TEXT)
        y += line_h

    # CTA chip — solid teal button with navy ink (a real button look)
    cta_f = font(FONTS / "HankenGrotesk.ttf", 32, [700])
    cta_txt = f"{cta}  →"
    tw = d.textlength(cta_txt, font=cta_f)
    chip_y = H - margin - 96
    NAVY_INK = (7, 18, 31)
    d.rounded_rectangle([margin, chip_y, margin + tw + 64, chip_y + 60], 30, fill=TEAL)
    d.text((margin + 32, chip_y + 13), cta_txt, font=cta_f, fill=NAVY_INK)

    # bottom bar: brand + site
    brand_f = font(FONTS / "HankenGrotesk.ttf", 36, [800])
    site_f = font(FONTS / "HankenGrotesk.ttf", 30, [600])
    d.text((margin, H - margin - 18), "SEO With Faiz", font=brand_f, fill=INK_TEXT)
    site_txt = "seowithfaiz.com"
    stw = d.textlength(site_txt, font=site_f)
    d.text((W - margin - stw, H - margin - 14), site_txt, font=site_f, fill=MUTED)

    out.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(out, "PNG", optimize=True)
    print(f"ad written: {out} ({out.stat().st_size // 1024}KB, {W}x{H})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--statement", required=True)
    ap.add_argument("--support", default="For boutique hotels")
    ap.add_argument("--cta", default="Free 10-minute site teardown")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    render(a.statement, a.support, a.cta,
           ROOT / a.out if not Path(a.out).is_absolute() else Path(a.out))


if __name__ == "__main__":
    main()
