#!/usr/bin/env python3
"""LinkedIn post graphic: "the nuclear update in digital marketing" (AI eating the click).

Deliberately OFF-brand palette per request: warm bone + ink + one vivid vermilion.
Editorial / risograph feel (flat color, no gradients, no glow) so it reads
human-designed rather than AI-generated. 1080x1080 square (best in the LI feed).
"""
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FONTS = Path(__file__).resolve().parent / "fonts"

BONE      = (243, 237, 226)
BONE_LT   = (250, 246, 239)
INK       = (23, 20, 18)
VERM      = (255, 72, 30)
GRAY      = (201, 193, 181)   # muted "old links" on bone
MUTED     = (124, 116, 105)


def font(name, size, var=None):
    f = ImageFont.truetype(str(FONTS / name), size)
    if var:
        try:
            f.set_variation_by_axes(var)
        except Exception:
            pass
    return f


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


def sparkle(d, cx, cy, r, fill):
    # 4-point star
    d.polygon([(cx, cy - r), (cx + r * 0.24, cy - r * 0.24),
               (cx + r, cy), (cx + r * 0.24, cy + r * 0.24),
               (cx, cy + r), (cx - r * 0.24, cy + r * 0.24),
               (cx - r, cy), (cx - r * 0.24, cy - r * 0.24)], fill=fill)


def render(out):
    W = H = 1080
    M = 96
    im = Image.new("RGB", (W, H), BONE)
    d = ImageDraw.Draw(im)

    # ── eyebrow pill ──
    eb_f = font("HankenGrotesk.ttf", 25, [800])
    eb = "THE NUCLEAR UPDATE"
    ew = d.textlength(eb, font=eb_f)
    d.rounded_rectangle([M, 112, M + ew + 56, 112 + 50], 25, fill=VERM)
    d.text((M + 28, 124), eb, font=eb_f, fill=BONE_LT)
    # tiny tracked date at right of pill
    dt_f = font("HankenGrotesk.ttf", 25, [700])
    dt = "DIGITAL MARKETING · 2026"
    d.text((W - M - d.textlength(dt, font=dt_f), 124), dt, font=dt_f, fill=MUTED)

    # ── headline (editorial serif) ──
    h_f = font("Fraunces.ttf", 90, [144, 600, 0, 0])
    y = 214
    for ln in wrap(d, "Search just stopped sending clicks.", h_f, W - M * 2):
        d.text((M, y), ln, font=h_f, fill=INK)
        y += 100

    # ── diagram: 10 blue links  →  1 AI answer ──
    lab_f = font("HankenGrotesk.ttf", 26, [800])
    dtop = 536
    d.text((M, dtop), "YESTERDAY", font=lab_f, fill=MUTED)

    # left: stack of muted "link" bars
    bar_y = dtop + 52
    widths = [300, 264, 288, 240, 300, 220, 276]
    for w in widths:
        d.rounded_rectangle([M, bar_y, M + w, bar_y + 13], 6, fill=GRAY)
        bar_y += 29
    left_bottom = bar_y - 16

    # right: single vermilion answer block
    bx0 = W - M - 322
    bx1 = W - M
    by0 = dtop + 52
    by1 = left_bottom
    d.text((bx0, dtop), "TODAY", font=lab_f, fill=VERM)
    d.rounded_rectangle([bx0, by0, bx1, by1], 26, fill=VERM)
    sparkle(d, bx0 + 40, by0 + 44, 15, BONE_LT)
    d.text((bx0 + 66, by0 + 26), "AI answer", font=font("HankenGrotesk.ttf", 32, [800]), fill=BONE_LT)
    for i, w in enumerate((248, 248, 176)):
        ly = by0 + 92 + i * 30
        d.rounded_rectangle([bx0 + 32, ly, bx0 + 32 + w, ly + 12], 6, fill=(255, 176, 158))

    # arrow between them (vermilion)
    ay = (by0 + by1) // 2
    ax0 = M + max(widths) + 34
    ax1 = bx0 - 30
    d.line([ax0, ay, ax1 - 10, ay], fill=VERM, width=11)
    d.polygon([(ax1, ay), (ax1 - 26, ay - 17), (ax1 - 26, ay + 17)], fill=VERM)

    # ── takeaway ──
    tk_f = font("HankenGrotesk.ttf", 41, [700])
    ty = by1 + 60
    d.text((M, ty), "The new game isn't ranking #1.", font=tk_f, fill=INK)
    ty += 54
    part1 = "It's being the source "
    d.text((M, ty), part1, font=tk_f, fill=INK)
    w1 = d.textlength(part1, font=tk_f)
    d.text((M + w1, ty), "AI quotes.", font=tk_f, fill=VERM)

    # ── footer ──
    d.line([M, H - 100, W - M, H - 100], fill=(220, 213, 201), width=2)
    wm_f = font("HankenGrotesk.ttf", 27, [800])
    d.text((M, H - 66), "SEO WITH FAIZ", font=wm_f, fill=INK)
    url_f = font("HankenGrotesk.ttf", 26, [600])
    d.text((W - M - d.textlength("seowithfaiz.com", font=url_f), H - 65),
           "seowithfaiz.com", font=url_f, fill=MUTED)

    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, "PNG", optimize=True)
    print(f"linkedin ai post: {out} ({out.stat().st_size // 1024}KB, {W}x{H})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="assets/social/li-ai-zeroclick.png")
    a = ap.parse_args()
    render(ROOT / a.out if not Path(a.out).is_absolute() else Path(a.out))


if __name__ == "__main__":
    main()
