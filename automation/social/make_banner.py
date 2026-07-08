#!/usr/bin/env python3
"""LinkedIn banner (1584x396) for SEO With Faiz — brand-matched.

Dark navy gradient, teal accent, dot grid, a globe-echo motif on the right
(tying to the site's 3D hero), Fraunces headline + Hanken support.
Content sits in the upper/center band, clear of the bottom-left avatar zone
LinkedIn overlays on a personal profile.
"""
from __future__ import annotations
import argparse
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
FONTS = Path(__file__).resolve().parent / "fonts"

W, H = 1584, 396
NAVY_TOP = (6, 14, 27)
NAVY_MID = (10, 33, 42)
NAVY_BOT = (8, 20, 40)
TEAL = (47, 212, 198)
INK = (233, 251, 248)
MUTED = (168, 194, 205)


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient():
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        t = y / (H - 1)
        c = lerp(NAVY_TOP, NAVY_MID, t / 0.55) if t < 0.55 else lerp(NAVY_MID, NAVY_BOT, (t - 0.55) / 0.45)
        for x in range(W):
            px[x, y] = c
    return im.convert("RGBA")


def font(path, size, axes=None):
    f = ImageFont.truetype(str(path), size)
    if axes:
        try:
            f.set_variation_by_axes(axes)
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
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render(out: Path):
    base = gradient()

    # teal glow, top-right
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W - 620, -320, W + 220, 360], fill=(47, 212, 198, 40))
    base = Image.alpha_composite(base, glow.filter(ImageFilter.GaussianBlur(150)))

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # dot grid
    for y in range(30, H, 40):
        for x in range(30, W, 40):
            d.ellipse([x, y, x + 2, y + 2], fill=(255, 255, 255, 10))

    # globe-echo: faint concentric dotted sphere, framed to the right so it
    # never competes with the centered message.
    cx, cy, R = W - 190, H // 2, 205
    for ring in range(6):
        rr = R - ring * 33
        if rr <= 0:
            continue
        n = max(18, int(rr / 4))
        for i in range(n):
            ang = (i / n) * 2 * math.pi
            x = cx + rr * math.cos(ang)
            y = cy + rr * math.sin(ang) * 0.62
            a = 46 if ring < 2 else 26
            d.ellipse([x - 1.5, y - 1.5, x + 1.5, y + 1.5], fill=(47, 212, 198, a))
    d.arc([cx - R, cy - int(R * 0.62), cx + R, cy + int(R * 0.62)], 205, 335,
          fill=(47, 212, 198, 60), width=2)

    base = Image.alpha_composite(base, overlay)
    d = ImageDraw.Draw(base)

    # ---- centered content: sits above the bottom-left avatar zone and
    #      survives LinkedIn's mobile center-crop ----
    CX = W // 2
    # kicker (centered, with flanking accent dashes)
    kick_f = font(FONTS / "HankenGrotesk.ttf", 25, [800])
    kick = "DESIGN · DEVELOPMENT · SEO · PERFORMANCE MARKETING"
    kw = d.textlength(kick, font=kick_f)
    d.text((CX, 50), kick, font=kick_f, fill=TEAL, anchor="ma")
    d.rounded_rectangle([CX - kw / 2 - 66, 60, CX - kw / 2 - 22, 64], 2, fill=TEAL)
    d.rounded_rectangle([CX + kw / 2 + 22, 60, CX + kw / 2 + 66, 64], 2, fill=TEAL)

    # headline (Fraunces), centered, sized to fit two lines cleanly
    head = "Websites engineered to be found — and to sell."
    size = 66
    while size > 40:
        hf = font(FONTS / "Fraunces.ttf", size, [72, 600, 0, 1])
        lines = wrap(d, head, hf, 1120)
        lh = int(size * 1.12)
        if len(lines) * lh <= 165:
            break
        size -= 3
    y = 100
    for ln in lines:
        d.text((CX, y), ln, font=hf, fill=INK, anchor="ma")
        y += lh

    # support line (Hanken), centered
    sup_f = font(FONTS / "HankenGrotesk.ttf", 26, [600])
    d.text((CX, y + 14), "Custom · 3D · Shopify Plus · WordPress · Magento · Technical & International SEO",
           font=sup_f, fill=MUTED, anchor="ma")

    # site url, teal, centered under support
    url_f = font(FONTS / "HankenGrotesk.ttf", 27, [800])
    d.text((CX, y + 52), "seowithfaiz.com", font=url_f, fill=TEAL, anchor="ma")

    out.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(out, "PNG", optimize=True)
    print(f"banner written: {out} ({out.stat().st_size // 1024}KB, {W}x{H})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="assets/social/linkedin-banner.png")
    a = ap.parse_args()
    render(ROOT / a.out if not Path(a.out).is_absolute() else Path(a.out))


if __name__ == "__main__":
    main()
