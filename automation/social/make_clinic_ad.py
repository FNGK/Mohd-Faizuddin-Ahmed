#!/usr/bin/env python3
"""Conversion-focused clinic ad creative for SEO With Faiz.

Direct-response upgrade over the plain text card: SHOWS the problem via a mock
Google Local Pack (competitors outranking the clinic), a hard on-image CTA, a
scarcity eyebrow, and a high-value deliverable name. 1080x1350 (4:5 feed).
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
FONTS = Path(__file__).resolve().parent / "fonts"

W, H = 1080, 1350
NAVY_TOP = (6, 14, 27)
NAVY_MID = (10, 33, 42)
NAVY_BOT = (8, 20, 40)
TEAL = (47, 212, 198)
INK = (232, 251, 248)
MUTED = (170, 195, 205)
CARD_BG = (245, 247, 245)
CARD_INK = (20, 28, 36)
CARD_MUTED = (92, 106, 114)
GOLD = (245, 183, 49)
RED = (226, 84, 78)
BLUE = (66, 133, 244)


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient():
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        t = y / (H - 1)
        c = lerp(NAVY_TOP, NAVY_MID, t / 0.5) if t < 0.5 else lerp(NAVY_MID, NAVY_BOT, (t - 0.5) / 0.5)
        for x in range(W):
            px[x, y] = c
    return im


def font(name, size, var=None):
    f = ImageFont.truetype(str(FONTS / name), size)
    if var:
        try:
            f.set_variation_by_axes(var)
        except Exception:
            pass
    return f


def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def wrap(d, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render(out):
    base = gradient().convert("RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W - 520, -320, W + 320, 520], fill=(47, 212, 198, 40))
    glow = glow.filter(ImageFilter.GaussianBlur(170))
    base = Image.alpha_composite(base, glow)
    d = ImageDraw.Draw(base)
    margin = 72

    # ── scarcity eyebrow (real: Faiz is solo, capacity is genuinely limited) ──
    eb_f = font("HankenGrotesk.ttf", 29, [800])
    eb1 = "FREE COMPETITOR TEARDOWN"
    d.text((margin, margin + 2), eb1, font=eb_f, fill=TEAL)
    w1 = d.textlength(eb1, font=eb_f)
    eb2_f = font("HankenGrotesk.ttf", 27, [600])
    d.text((margin + w1 + 12, margin + 5), "(only 3 spots this week)", font=eb2_f, fill=MUTED)

    # ── headline ──
    hy = margin + 86
    h_f = font("Fraunces.ttf", 54, [72, 600, 0, 1])
    hl = "Patients search 'skin clinic near me' — and find your rival."
    for ln in wrap(d, hl, h_f, W - margin * 2):
        d.text((margin, hy), ln, font=h_f, fill=INK)
        hy += int(54 * 1.16)

    # ── mock Google Local Pack (SHOW the problem) ──
    cx0, cy0, cx1 = margin, hy + 26, W - margin
    cy1 = cy0 + 556
    # soft shadow
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([cx0, cy0 + 10, cx1, cy1 + 14], 28, fill=(0, 0, 0, 70))
    base = Image.alpha_composite(base, sh.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([cx0, cy0, cx1, cy1], 28, fill=CARD_BG)
    pad = 34

    sb_y = cy0 + pad
    d.rounded_rectangle([cx0 + pad, sb_y, cx1 - pad, sb_y + 60], 16, fill=(255, 255, 255),
                        outline=(212, 218, 216), width=2)
    mgx, mgy = cx0 + pad + 32, sb_y + 30
    d.ellipse([mgx - 11, mgy - 11, mgx + 7, mgy + 7], outline=CARD_MUTED, width=4)
    d.line([mgx + 6, mgy + 6, mgx + 15, mgy + 15], fill=CARD_MUTED, width=4)
    d.text((cx0 + pad + 60, sb_y + 15), "skin clinic near me", font=font("HankenGrotesk.ttf", 29, [500]), fill=CARD_MUTED)

    clinics = [
        ("Radiance Skin & Laser Clinic", "4.8", "(412)"),
        ("Dermacare Aesthetics", "4.7", "(356)"),
        ("The Glow Skin Clinic", "4.6", "(289)"),
    ]
    name_f = font("HankenGrotesk.ttf", 32, [700])
    rate_f = font("HankenGrotesk.ttf", 26, [500])
    pin_f = font("HankenGrotesk.ttf", 27, [800])
    ry = sb_y + 88
    for i, (nm, rt, rev) in enumerate(clinics):
        pcx, pcy = cx0 + pad + 22, ry + 26
        d.ellipse([pcx - 20, pcy - 20, pcx + 20, pcy + 20], fill=BLUE)
        num = str(i + 1)
        nw = d.textlength(num, font=pin_f)
        d.text((pcx - nw / 2, pcy - 18), num, font=pin_f, fill=(255, 255, 255))
        d.text((cx0 + pad + 58, ry + 1), nm, font=name_f, fill=CARD_INK)
        star(d, cx0 + pad + 66, ry + 50, 12, GOLD)
        d.text((cx0 + pad + 86, ry + 38), rt + "  " + rev + "   ·   Open now", font=rate_f, fill=CARD_MUTED)
        ry += 90
        if i < 2:
            d.line([cx0 + pad, ry - 6, cx1 - pad, ry - 6], fill=(228, 232, 230), width=2)

    # red-tinted alert box for the "your clinic" row (adopted from the redesign
    # — the strongest emphasis idea it had, now rebuilt on-brand).
    bx0, by0, bx1, by1 = cx0 + pad - 8, ry + 4, cx1 - pad + 8, ry + 100
    d.rounded_rectangle([bx0, by0, bx1, by1], 16, fill=(252, 227, 225), outline=RED, width=2)
    yy = by0 + 12
    pcx, pcy = bx0 + 30, yy + 26
    d.ellipse([pcx - 20, pcy - 20, pcx + 20, pcy + 20], fill=RED)
    d.line([pcx - 8, pcy - 8, pcx + 8, pcy + 8], fill=(255, 255, 255), width=5)
    d.line([pcx - 8, pcy + 8, pcx + 8, pcy - 8], fill=(255, 255, 255), width=5)
    d.text((pcx + 38, yy + 1), "Your clinic — not in the top results.", font=font("HankenGrotesk.ttf", 32, [800]), fill=(181, 45, 40))
    d.text((pcx + 38, yy + 41), "They book a competitor before they ever find you.", font=rate_f, fill=(150, 78, 74))

    # ── hard CTA (on-image directive) ──
    cta_y = cy1 + 44
    cta_f = font("HankenGrotesk.ttf", 36, [800])
    cta = "Tap  ‘Send Message’  →  free teardown"
    ctw = d.textlength(cta, font=cta_f)
    px0 = (W - (ctw + 76)) // 2
    d.rounded_rectangle([px0, cta_y, px0 + ctw + 76, cta_y + 74], 37, fill=TEAL)
    d.text((px0 + 38, cta_y + 16), cta, font=cta_f, fill=(4, 35, 31))

    del_f = font("HankenGrotesk.ttf", 26, [500])
    dl = "A real Local SEO & competitor teardown — not an auto PDF."
    dlw = d.textlength(dl, font=del_f)
    d.text(((W - dlw) // 2, cta_y + 96), dl, font=del_f, fill=MUTED)

    tr_f = font("HankenGrotesk.ttf", 25, [700])
    tr = "Founder-led   ·   not an agency   ·   reply within 24h"
    trw = d.textlength(tr, font=tr_f)
    d.text(((W - trw) // 2, cta_y + 196), tr, font=tr_f, fill=(120, 205, 195))

    d.text((margin, H - margin - 28), "SEO With Faiz", font=font("HankenGrotesk.ttf", 32, [800]), fill=INK)
    st = "seowithfaiz.com"
    sf = font("HankenGrotesk.ttf", 28, [600])
    d.text((W - margin - d.textlength(st, font=sf), H - margin - 25), st, font=sf, fill=MUTED)

    out.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(out, "PNG", optimize=True)
    print(f"clinic ad: {out} ({out.stat().st_size // 1024}KB, {W}x{H})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    render(ROOT / a.out if not Path(a.out).is_absolute() else Path(a.out))


if __name__ == "__main__":
    main()
