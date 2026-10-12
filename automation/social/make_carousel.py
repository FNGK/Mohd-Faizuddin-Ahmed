#!/usr/bin/env python3
"""Carousel renderer for SEO With Faiz — info-on-image, varied layouts.

Builds a multi-slide Instagram/LinkedIn carousel (1080x1350, 4:5) from a JSON
spec. Each slide lays a clear marketing message OVER a topic-matched image
(Canva `generate-image` output) with a strong per-zone scrim so the text reads
on ANY photo, light or dark. Brand consistency comes from the TYPE SYSTEM
(Fraunces headline + Hanken support), a small corner signature, and progress
dots — never from forcing the site's navy/teal onto the picture.

This is the carousel companion to:
  - make_social_image.py  (single clean photo + corner signature, no message)
  - make_card.py          (single info card: statement over image/gradient)

Slide kinds (dispatch on "kind", default "point"):
  cover  — hook: kicker + big headline + sub. The thumb-stopper.
  point  — numbered teaching slide: index + headline + body.
  stat   — a single number the eye lands on + context.
  quote  — a one-line contrarian POV, large, centered.
  cta    — close: headline + body + url, teal accent.

Spec (JSON):
{
  "slug": "2026-10-12-shopify-probably-not",
  "handle": "@seo_with_faiz",
  "slides": [
    {"kind":"cover","image":"/abs/cover.jpg","kicker":"PLATFORM TRUTH",
     "headline":"When basic Shopify is already enough","sub":"A 60-second honesty check"},
    {"kind":"point","image":"/abs/1.jpg","n":"01",
     "headline":"Tiny catalog, simple needs","body":"A handful of SKUs and no custom checkout? Basic Shopify is not a compromise. It is the right call."},
    {"kind":"stat","image":"/abs/2.jpg","stat":"15-25%",
     "headline":"is what OTAs and over-built stacks quietly cost you","body":"Complexity you do not need is a tax, not a feature."},
    {"kind":"cta","image":"/abs/3.jpg",
     "headline":"Pick the tool the job needs","body":"Not the biggest one on the bench.","url":"seowithfaiz.com"}
  ]
}

A slide with no "image" falls back to a procedural navy gradient (so a run
never hard-fails if one generation is missing).

Usage:
  python automation/social/make_carousel.py \
      --spec /tmp/carousel.json \
      --out-dir assets/social/carousels/2026-10-12-shopify-probably-not
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
FONTS = Path(__file__).resolve().parent / "fonts"
LOGO = ROOT / "assets" / "social" / "brand" / "icon-mark.png"

W, H = 1080, 1350
MARGIN = 96

INK = (245, 250, 252)
MUTED = (198, 212, 222)
TEAL = (47, 212, 198)
NAVY = (6, 14, 27)
NAVY_MID = (10, 33, 42)


# ---- primitives ------------------------------------------------------------

def font(path, size, variation=None):
    f = ImageFont.truetype(str(path), size)
    if variation:
        try:
            f.set_variation_by_axes(variation)
        except Exception:
            pass
    return f


def FR(size, wght=600, opsz=72):          # Fraunces, the statement face
    return font(FONTS / "Fraunces.ttf", size, [opsz, wght, 0, 1])


def HK(size, wght=600):                    # Hanken Grotesk, the support face
    return font(FONTS / "HankenGrotesk.ttf", size, [wght])


def cover_resize(img, w, h):
    sw, sh = img.size
    scale = max(w / sw, h / sh)
    nw, nh = round(sw * scale), round(sh * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return img.crop((left, top, left + w, top + h))


def gradient_bg():
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        t = y / (H - 1)
        c = tuple(round(NAVY[i] + (NAVY_MID[i] - NAVY[i]) * min(1.0, t / 0.6)) for i in range(3))
        for x in range(W):
            px[x, y] = c
    return im.convert("RGBA")


# Design-led backgrounds (no photo): premium, varied-but-coherent. Dark tones
# so white type pops; a soft accent glow rotates per slide for &Walsh-style
# colour confidence without a clumsy stock photo.
DESIGN_TONES = [(6, 14, 27), (9, 20, 30), (13, 14, 26), (7, 22, 24)]      # navy·slate·plum·teal-black
GLOW_ACCENTS = [(47, 212, 198), (242, 184, 92), (236, 120, 110), (150, 132, 240)]  # teal·amber·coral·violet


def design_bg(idx):
    top = DESIGN_TONES[idx % len(DESIGN_TONES)]
    bot = tuple(max(0, c - 5) for c in top)
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        t = y / (H - 1)
        c = tuple(round(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        for x in range(W):
            px[x, y] = c
    base = im.convert("RGBA")
    acc = GLOW_ACCENTS[idx % len(GLOW_ACCENTS)]
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W - 540, -340, W + 320, 520], fill=(*acc, 48))
    base = Image.alpha_composite(base, glow.filter(ImageFilter.GaussianBlur(170)))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for yy in range(64, H, 54):
        for xx in range(64, W, 54):
            od.ellipse([xx, yy, xx + 2, yy + 2], fill=(255, 255, 255, 10))
    return Image.alpha_composite(base, ov)


def load_bg(slide, idx):
    """Priority: design-led background (style=='design' or no image) → clean,
    on-brand, never clumsy. A real photo (screenshot/work/proof) is used only
    when explicitly supplied and readable."""
    if slide.get("style") != "design":
        p = slide.get("image")
        if p:
            fp = Path(p) if Path(p).is_absolute() else ROOT / p
            if fp.exists():
                try:
                    return cover_resize(Image.open(fp).convert("RGBA"), W, H)
                except Exception:
                    pass
    return design_bg(idx)


def zone_scrim(base, top_frac, strength=210):
    """Vertical scrim darkest toward the bottom, fading out above `top_frac`.
    Keeps the picture visible up top while guaranteeing text legibility in the
    lower band where copy lives."""
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gp = grad.load()
    start = int(H * top_frac)
    for y in range(start, H):
        t = (y - start) / max(1, (H - start))
        a = int(strength * (t ** 1.25))
        row = (*NAVY, a)
        for x in range(W):
            gp[x, y] = row
    return Image.alpha_composite(base, grad)


def flat_veil(base, alpha=70):
    """A light even darken over the whole frame so bright images don't blow out
    the type. Cheap global contrast insurance."""
    return Image.alpha_composite(base, Image.new("RGBA", (W, H), (*NAVY, alpha)))


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


def draw_block(d, text, fnt, fill, x, y, max_w, leading=1.16):
    lines = wrap(d, text, fnt, max_w)
    lh = int(fnt.size * leading)
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def fit_block(d, text, face_fn, start, floor, wght, max_w, max_h, leading=1.14):
    """Shrink a headline until it fits max_h. Returns (font, lines, line_h)."""
    size = start
    while size >= floor:
        f = face_fn(size, wght)
        lines = wrap(d, text, f, max_w)
        lh = int(size * leading)
        if len(lines) * lh <= max_h:
            return f, lines, lh
        size -= 3
    f = face_fn(floor, wght)
    return f, wrap(d, text, f, max_w), int(floor * leading)


# ---- chrome (on every slide) ----------------------------------------------

def signature(base, d, handle, idx, total):
    pad = MARGIN
    icon = 52
    ix, iy = pad, H - pad - icon
    if LOGO.exists():
        logo = Image.open(LOGO).convert("RGBA").resize((icon, icon), Image.LANCZOS)
        base.paste(logo, (ix, iy), logo)
    else:
        cx, cy, r = ix + icon / 2, iy + icon / 2, icon / 2
        pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
               for a in range(-90, 270, 60)]
        d.polygon(pts, outline=TEAL, width=3)
    tx = ix + icon + 16
    d.text((tx, iy + 1), "SEO With Faiz", font=HK(26, 800), fill=INK)
    d.text((tx, iy + 28), handle, font=HK(18, 600), fill=MUTED)

    # progress dots, bottom-right
    if total > 1:
        dot, gap = 9, 9
        total_w = total * dot + (total - 1) * gap
        dx = W - pad - total_w
        dy = H - pad - icon // 2 - dot // 2
        for i in range(total):
            fill = TEAL if i == idx else (255, 255, 255, 90)
            d.ellipse([dx, dy, dx + dot, dy + dot], fill=fill)
            dx += dot + gap

    # "swipe" affordance on the cover — top-right chip so it never collides
    # with the progress dots (which live bottom-right) and reads on any image
    if total > 1 and idx == 0:
        swipe = "Swipe →"
        f = HK(22, 800)
        tw = d.textlength(swipe, font=f)
        x0 = W - pad - tw - 30
        y0 = pad - 8
        d.rounded_rectangle([x0 - 18, y0 - 10, x0 + tw + 18, y0 + 38], 24,
                            fill=(*NAVY, 150))
        d.text((x0, y0), swipe, font=f, fill=TEAL)


def kicker(d, text, x, y):
    d.rounded_rectangle([x, y + 7, x + 52, y + 13], 3, fill=TEAL)
    d.text((x + 70, y - 6), text.upper(), font=HK(28, 800), fill=TEAL)


# ---- slide layouts ---------------------------------------------------------

def slide_cover(base, s):
    base = zone_scrim(flat_veil(base, 60), 0.30, 230)
    d = ImageDraw.Draw(base)
    maxw = W - MARGIN * 2
    if s.get("kicker"):
        kicker(d, s["kicker"], MARGIN, int(H * 0.46))
    f, lines, lh = fit_block(d, s.get("headline", ""), FR, 96, 58, 600, maxw, 460)
    y = H - MARGIN - 150 - len(lines) * lh
    for ln in lines:
        d.text((MARGIN, y), ln, font=f, fill=INK)
        y += lh
    if s.get("sub"):
        draw_block(d, s["sub"], HK(34, 500), MUTED, MARGIN, y + 14, maxw)
    return base, d


def slide_point(base, s):
    base = zone_scrim(flat_veil(base, 55), 0.34, 225)
    d = ImageDraw.Draw(base)
    maxw = W - MARGIN * 2
    if s.get("n"):
        d.text((MARGIN, int(H * 0.40)), s["n"], font=FR(120, 500), fill=TEAL)
    f, lines, lh = fit_block(d, s.get("headline", ""), FR, 76, 48, 600, maxw, 300)
    y = int(H * 0.40) + 150
    for ln in lines:
        d.text((MARGIN, y), ln, font=f, fill=INK)
        y += lh
    if s.get("body"):
        draw_block(d, s["body"], HK(34, 400), MUTED, MARGIN, y + 16, maxw, 1.3)
    return base, d


def slide_stat(base, s):
    base = zone_scrim(flat_veil(base, 60), 0.30, 230)
    d = ImageDraw.Draw(base)
    maxw = W - MARGIN * 2
    stat = s.get("stat", "")
    sf = FR(190, 600)
    # shrink the stat if it is wide (e.g. "15-25%")
    while d.textlength(stat, font=sf) > maxw and sf.size > 90:
        sf = FR(sf.size - 8, 600)
    y = int(H * 0.42)
    d.text((MARGIN, y), stat, font=sf, fill=TEAL)
    y += int(sf.size * 1.02)
    y = draw_block(d, s.get("headline", ""), FR(44, 600), INK, MARGIN, y, maxw, 1.12)
    if s.get("body"):
        draw_block(d, s["body"], HK(32, 400), MUTED, MARGIN, y + 14, maxw, 1.3)
    return base, d


def slide_quote(base, s):
    base = flat_veil(base, 120)
    base = zone_scrim(base, 0.0, 90)
    d = ImageDraw.Draw(base)
    maxw = W - MARGIN * 2
    d.text((MARGIN, int(H * 0.22)), "“", font=FR(160, 600), fill=TEAL)
    f, lines, lh = fit_block(d, s.get("headline", ""), FR, 72, 44, 500, maxw, 560)
    y = (H - len(lines) * lh) // 2 + 30
    for ln in lines:
        d.text((MARGIN, y), ln, font=f, fill=INK)
        y += lh
    return base, d


def slide_cta(base, s):
    base = zone_scrim(flat_veil(base, 70), 0.26, 235)
    d = ImageDraw.Draw(base)
    maxw = W - MARGIN * 2
    f, lines, lh = fit_block(d, s.get("headline", ""), FR, 84, 52, 600, maxw, 360)
    y = int(H * 0.46)
    for ln in lines:
        d.text((MARGIN, y), ln, font=f, fill=INK)
        y += lh
    if s.get("body"):
        y = draw_block(d, s["body"], HK(36, 500), MUTED, MARGIN, y + 16, maxw, 1.25)
    url = s.get("url", "seowithfaiz.com")
    d.rounded_rectangle([MARGIN, y + 30, MARGIN + 44, y + 36], 3, fill=TEAL)
    d.text((MARGIN + 62, y + 18), url, font=HK(34, 800), fill=TEAL)
    return base, d


def slide_list(base, s):
    """A scannable checklist/framework slide — the B2B 'mini-whitepaper' workhorse."""
    base = zone_scrim(flat_veil(base, 30), 0.0, 60)
    d = ImageDraw.Draw(base)
    maxw = W - MARGIN * 2
    y = int(H * 0.12)
    if s.get("kicker"):
        kicker(d, s["kicker"], MARGIN, y)
        y += 72
    f, lines, lh = fit_block(d, s.get("headline", ""), FR, 62, 42, 600, maxw, 190)
    for ln in lines:
        d.text((MARGIN, y), ln, font=f, fill=INK)
        y += lh
    y += 30
    for i, item in enumerate(s.get("items", [])[:5], 1):
        d.ellipse([MARGIN, y + 6, MARGIN + 34, y + 40], outline=TEAL, width=3)
        d.text((MARGIN + 9, y + 7), str(i), font=HK(22, 800), fill=TEAL)
        end = draw_block(d, item, HK(33, 500), INK, MARGIN + 56, y + 2, maxw - 56, 1.22)
        y = end + 22
    return base, d


LAYOUTS = {
    "cover": slide_cover,
    "point": slide_point,
    "stat": slide_stat,
    "quote": slide_quote,
    "cta": slide_cta,
    "list": slide_list,
}


def render_slide(s, idx, total, handle):
    base = load_bg(s, idx)
    layout = LAYOUTS.get(s.get("kind", "point"), slide_point)
    base, d = layout(base, s)
    signature(base, d, handle, idx, total)
    return base.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="JSON carousel spec.")
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()

    spec_path = Path(a.spec) if Path(a.spec).is_absolute() else ROOT / a.spec
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    handle = spec.get("handle", "@seo_with_faiz")
    slides = spec["slides"]
    total = len(slides)

    out_dir = Path(a.out_dir) if Path(a.out_dir).is_absolute() else ROOT / a.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    written = []
    for i, s in enumerate(slides):
        img = render_slide(s, i, total, handle)
        out = out_dir / f"slide-{i + 1:02d}.png"
        img.save(out, "PNG", optimize=True)
        written.append(out)
    kb = sum(p.stat().st_size for p in written) // 1024
    print(f"carousel written: {len(written)} slides in {out_dir} ({kb}KB total)")
    for p in written:
        print(f"  {p.name}  ({p.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main()
