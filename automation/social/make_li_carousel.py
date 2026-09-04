#!/usr/bin/env python3
"""3-slide LinkedIn POV carousel: 'Ranking #1 is now a vanity metric.'

Off-brand by request: warm obsidian + one electric-chartreuse accent + off-white,
with subtle film grain (an anti-AI, analog signal). Editorial serif statements
(Fraunces) against a grotesk (Hanken). 1080x1350 portrait (max LI feed height).
No meta-labels — the statements carry the slides.

  --slide 1|2|3   render one PNG
  --pdf           render all three + a combined document-carousel PDF
"""
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FONTS = Path(__file__).resolve().parent / "fonts"
OUTDIR = ROOT / "assets/social"

BG     = (19, 17, 16)
WHITE  = (244, 240, 232)
MUTED  = (166, 160, 149)
BODY   = (214, 209, 199)
CHART  = (214, 255, 61)
INKON  = (16, 18, 6)     # dark text on chartreuse


def font(name, size, var=None):
    f = ImageFont.truetype(str(FONTS / name), size)
    if var:
        try:
            f.set_variation_by_axes(var)
        except Exception:
            pass
    return f


def grain(im, amount=0.05):
    noise = Image.effect_noise(im.size, 26).convert("RGB")
    return Image.blend(im, noise, amount)


def draw_rich(d, text, fnt, maxw, x0, y0, lh, base, acc):
    """Word-wrap; words prefixed with § render in the accent color."""
    space = d.textlength(" ", font=fnt)
    lines, cur, curw = [], [], 0
    for w in text.split():
        af = w.startswith("§")
        ww = w[1:] if af else w
        tw = d.textlength(ww, font=fnt)
        if cur and curw + space + tw > maxw:
            lines.append(cur)
            cur, curw = [], 0
        if cur:
            curw += space
        cur.append((ww, af, tw))
        curw += tw
    if cur:
        lines.append(cur)
    y = y0
    for line in lines:
        x = x0
        for i, (ww, af, tw) in enumerate(line):
            if i:
                x += space
            d.text((x, y), ww, font=fnt, fill=(acc if af else base))
            x += tw
        y += lh
    return y


def topbar(d, W, M, idx):
    d.text((M, 66), "SEO WITH FAIZ", font=font("HankenGrotesk.ttf", 24, [800]), fill=WHITE)
    ix = f"{idx} / 03"
    f2 = font("HankenGrotesk.ttf", 24, [800])
    d.text((W - M - d.textlength(ix, font=f2), 66), ix, font=f2, fill=CHART)


def build(slide):
    W, H, M = 1080, 1080, 90   # 1:1 square — fills LinkedIn's document viewer
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    topbar(d, W, M, slide)

    if slide == 1:
        st = font("Fraunces.ttf", 94, [144, 600, 0, 0])
        draw_rich(d, "Ranking #1 on Google is now a §vanity §metric.",
                  st, W - 2 * M, M, 268, 106, WHITE, CHART)
        d.text((M, 946), "Swipe for the part nobody's pricing in",
               font=font("HankenGrotesk.ttf", 29, [600]), fill=MUTED)
        d.text((M, 984), "SWIPE  →", font=font("HankenGrotesk.ttf", 30, [800]), fill=CHART)

    elif slide == 2:
        st = font("Fraunces.ttf", 60, [144, 600, 0, 0])
        ny = draw_rich(d, "You're not being outranked. You're being §left §out §of §the §answer.",
                       st, W - 2 * M, M, 196, 72, WHITE, CHART)
        body = ("Your buyer stopped scrolling ten blue links. They ask "
                "ChatGPT, Perplexity, or Google's AI for the best option, "
                "and they act on the three names it returns.\n\n"
                "If the model doesn't cite you, you're invisible to that "
                "buyer. Your #1 ranking never enters the room.")
        by = ny + 62
        bf = font("HankenGrotesk.ttf", 31, [500])
        for para in body.split("\n\n"):
            by = draw_rich(d, para, bf, W - 2 * M, M, by, 45, BODY, CHART) + 24

    else:  # slide 3
        st = font("Fraunces.ttf", 70, [144, 600, 0, 0])
        ny = draw_rich(d, "I make brands the §answer §AI §gives.",
                       st, W - 2 * M, M, 200, 84, WHITE, CHART)
        body = ("Not keywords. Not blog volume. I engineer how language "
                "models read, trust, and cite your brand, so you show up "
                "the moment a buyer asks.\n\n"
                "If your website is revenue infrastructure, this is the "
                "gap I close.")
        by = ny + 58
        bf = font("HankenGrotesk.ttf", 31, [500])
        for para in body.split("\n\n"):
            by = draw_rich(d, para, bf, W - 2 * M, M, by, 45, BODY, CHART) + 22

        d.text((M, 862), "See where your brand stands",
               font=font("HankenGrotesk.ttf", 29, [600]), fill=MUTED)
        pill_f = font("HankenGrotesk.ttf", 36, [800])
        label = "seowithfaiz.com  →"
        pw = d.textlength(label, font=pill_f)
        d.rounded_rectangle([M, 908, M + pw + 68, 908 + 76], 38, fill=CHART)
        d.text((M + 34, 924), label, font=pill_f, fill=INKON)

    return grain(im, 0.05)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slide", type=int, choices=[1, 2, 3])
    ap.add_argument("--pdf", action="store_true")
    a = ap.parse_args()
    OUTDIR.mkdir(parents=True, exist_ok=True)

    if a.pdf:
        imgs = [build(s) for s in (1, 2, 3)]
        for i, im in enumerate(imgs, 1):
            im.save(OUTDIR / f"li-vanity-{i}.png", "PNG", optimize=True)
        pdf = OUTDIR / "li-vanity-carousel.pdf"
        imgs[0].save(pdf, "PDF", save_all=True, append_images=imgs[1:], resolution=72.0)
        print(f"carousel PDF: {pdf} ({pdf.stat().st_size // 1024}KB, 3 pages 1080x1350)")
    else:
        s = a.slide or 1
        out = OUTDIR / f"li-vanity-{s}.png"
        build(s).save(out, "PNG", optimize=True)
        print(f"slide {s}: {out}")


if __name__ == "__main__":
    main()
