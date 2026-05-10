"""Render branded 1200x630 Open Graph image with logo on gradient canvas.

Logo asset requirements (see assets/logos/LOCKUP_IMAGE_EDIT_PROMPT.txt for full brief):
  - PNG with alpha; artwork should blend on BOTH near-white (#f8fafc) chips AND
    dark navy chips (#111b2e–#152338) without harsh light halos.
  - Primary brand teal aligned to site CSS: ~#0f766e (light theme); luminous
    teal ~#2dd4bf reads well on dark surfaces.
  - Avoid pure RGB white boxes behind lettering; use transparent blend or
    subtle noise matched to UI surfaces so multiply/plus-lighter CSS blends work.

Regenerate og-default.png after replacing assets/logos/seo-with-faiz-logo-technical-precision-revenue-growth.png:
  python automation/build_og_image.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
LOGO = ROOT / "assets" / "logos" / "seo-with-faiz-logo-technical-precision-revenue-growth.png"
OUT = ROOT / "assets" / "og" / "og-default.png"
W, H = 1200, 630


def gradient_rgb(y: int, h: int) -> tuple[int, int, int]:
    t = y / max(h - 1, 1)
    c0 = (15, 23, 42)
    c1 = (15, 118, 110)
    c2 = (30, 64, 110)
    if t < 0.45:
        u = t / 0.45
        return tuple(int(a + (b - a) * u) for a, b in zip(c0, c1))
    u = (t - 0.45) / 0.55
    return tuple(int(a + (b - a) * u) for a, b in zip(c1, c2))


def pick_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("arial.ttf", "segoeui.ttf", "calibri.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> None:
    if not LOGO.is_file():
        raise SystemExit(f"Missing logo: {LOGO}")

    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        row = gradient_rgb(y, H)
        for x in range(W):
            px[x, y] = row

    draw = ImageDraw.Draw(img)
    step = 56
    line = (51, 65, 85)
    for x in range(0, W, step):
        draw.line([(x, 0), (x, H)], fill=line, width=1)
    for y in range(0, H, step):
        draw.line([(0, y), (W, y)], fill=line, width=1)

    logo = Image.open(LOGO).convert("RGBA")
    lw, lh = logo.size
    target_w = min(int(W * 0.58), lw * 3)
    scale = target_w / lw
    target_h = int(lh * scale)
    logo = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)

    lx = (W - target_w) // 2
    ly = (H - target_h) // 2 - 36

    pad_x, pad_y = 36, 28
    chip_w, chip_h = target_w + pad_x * 2, target_h + pad_y * 2
    chip = Image.new("RGBA", (chip_w, chip_h), (248, 250, 252, 252))
    chip_draw = ImageDraw.Draw(chip)
    chip_draw.rounded_rectangle([0, 0, chip_w - 1, chip_h - 1], radius=20, outline=(203, 213, 225), width=2)
    chip.paste(logo, (pad_x, pad_y), logo)

    cx = (W - chip_w) // 2
    cy = ly - pad_y
    img.paste(chip, (cx, cy), chip)

    font = pick_font(26)
    font_sm = pick_font(21)
    tag = "Technical precision · Revenue growth · White-hat SEO"
    bbox = draw.textbbox((0, 0), tag, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (W - tw) // 2
    ty = H - 78
    draw.rounded_rectangle([tx - 18, ty - 12, tx + tw + 18, ty + th + 12], radius=14, fill=(15, 23, 42))
    draw.text((tx, ty), tag, fill=(241, 245, 249), font=font)

    sub = "Pipeline-focused SEO · Data-led decisions · Long-term authority"
    bbox2 = draw.textbbox((0, 0), sub, font=font_sm)
    sw = bbox2[2] - bbox2[0]
    sx = (W - sw) // 2
    sy = ty + th + 22
    draw.text((sx, sy), sub, fill=(203, 213, 225), font=font_sm)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
