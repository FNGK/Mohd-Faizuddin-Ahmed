#!/usr/bin/env python3
"""Optimize images and apply sitewide performance patches (PageSpeed / Lighthouse)."""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SKIP = {
    ROOT / "Professional_Resume.html",
    ROOT / "automation" / "blog" / "admin" / "review.html",
}

FONT_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Fraunces:opsz,wght@9..144,500;600;700;800&"
    "family=Manrope:wght@400;500;600;700;800&display=swap"
)

LOGO_LIGHT = "seo-with-faiz-logo-technical-precision-revenue-growth.png"
LOGO_DARK = "seo-with-faiz-logo-dark-mode-technical-precision-revenue-growth.png"
LOGO_ALT = (
    "SEO With Faiz logo — technical SEO and revenue growth services; shield mark with "
    "code, bridge, and growth chart (transparent PNG for light mode)."
)

RASTER_ASSETS = [
    ("assets/projects/telangana-stride-hub.jpg", 640, 85),
    ("assets/projects/unstop-seo-audit.png", 640, 82),
    ("assets/projects/lighthouse-global-scores-proof.png", 640, 82),
    ("assets/projects/100hires.png", 640, 82),
    ("assets/profile/faiz-headshot.png", 360, 85),
]


def resize_width(img: Image.Image, max_width: int) -> Image.Image:
    if img.width <= max_width:
        return img
    ratio = max_width / img.width
    size = (max_width, max(1, round(img.height * ratio)))
    return img.resize(size, Image.Resampling.LANCZOS)


def save_webp_and_png(src: Path, out_stem: Path, max_width: int, quality: int) -> tuple[int, int]:
    img = Image.open(src)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    img = resize_width(img, max_width)
    out_stem.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_stem.with_suffix(".webp"), "WEBP", quality=quality, method=6)
    png = img.convert("RGBA") if img.mode == "RGBA" else img.convert("RGB")
    png.save(out_stem.with_suffix(".png"), "PNG", optimize=True)
    return img.width, img.height


def save_webp_only(src: Path, max_width: int, quality: int) -> None:
    img = Image.open(src)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    img = resize_width(img, max_width)
    out = src.with_suffix(".webp")
    img.save(out, "WEBP", quality=quality, method=6)
    print(f"webp {out.relative_to(ROOT)}")


def optimize_images() -> None:
    for rel, width, quality in RASTER_ASSETS:
        src = ROOT / rel
        if not src.exists():
            continue
        save_webp_only(src, width, quality)


def prefix_for(path: Path) -> str:
    depth = len(path.relative_to(ROOT).parts) - 1
    return "./" if depth == 0 else "../" * depth


def performance_head(prefix: str, *, preload_logo: bool) -> str:
    lines = [
        f'  <link rel="icon" href="{prefix}assets/logos/seowithfaiz-icon.svg" type="image/svg+xml">',
        '  <link rel="preconnect" href="https://fonts.googleapis.com">',
        '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        f'  <link rel="preload" as="style" href="{FONT_URL}" onload="this.onload=null;this.rel=\'stylesheet\'">',
        f'  <noscript><link rel="stylesheet" href="{FONT_URL}"></noscript>',
    ]
    if preload_logo:
        lines.insert(
            4,
            f'  <link rel="preload" as="image" href="{prefix}assets/logos/{LOGO_LIGHT}">',
        )
    return "\n".join(lines) + "\n"


def strip_old_head_bits(html: str) -> str:
    html = re.sub(
        r'\s*<link rel="icon" href="[^"]*seowithfaiz-icon\.svg"[^>]*>\n?',
        "",
        html,
    )
    html = re.sub(
        r'\s*<link rel="preconnect" href="https://fonts\.googleapis\.com">\n?',
        "",
        html,
    )
    html = re.sub(
        r'\s*<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\n?',
        "",
        html,
    )
    return html


def patch_head(html: str, path: Path) -> str:
    html = strip_old_head_bits(html)
    prefix = prefix_for(path)
    preload = path.name == "index.html" and path.parent == ROOT
    block = performance_head(prefix, preload_logo=preload)
    needle = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
    if needle not in html:
        return html
    return html.replace(needle, needle + "\n" + block, 1)


def brand_block(prefix: str, *, high_priority: bool) -> str:
    prio = ' fetchpriority="high"' if high_priority else ""
    return (
        f'      <a class="brand" href="{prefix}index.html" aria-label="SEO With Faiz home">\n'
        f'        <img class="brand-logo brand-logo--light" src="{prefix}assets/logos/{LOGO_LIGHT}" '
        f'alt="{LOGO_ALT}" width="1024" height="498" decoding="async"{prio}>\n'
        f'        <img class="brand-logo brand-logo--dark" src="{prefix}assets/logos/{LOGO_DARK}" alt="" '
        f'width="580" height="228" decoding="async" aria-hidden="true">\n'
        f"      </a>"
    )


def patch_brand(html: str, path: Path) -> str:
    prefix = prefix_for(path)
    high = path.name == "index.html" and path.parent == ROOT
    brand_href = f"{prefix}index.html"
    block = brand_block(prefix, high_priority=high)
    block = block.replace(f'href="{prefix}index.html"', f'href="{brand_href}"', 1)

    pattern = re.compile(
        r'<a class="brand" href="[^"]*" aria-label="SEO With Faiz home">'
        r'\s*<img class="brand-logo brand-logo--light"[^>]*>\s*'
        r'<img class="brand-logo brand-logo--dark"[^>]*>\s*'
        r"</a>",
        re.DOTALL,
    )
    if not pattern.search(html):
        # Already picture-based or different layout
        pattern2 = re.compile(
            r'<a class="brand" href="[^"]*" aria-label="SEO With Faiz home">[\s\S]*?</a>',
            re.DOTALL,
        )
        return pattern2.sub(block, html, count=1)
    return pattern.sub(block, html, count=1)


def picture_img(prefix: str, rel_path: str, alt: str, width: int, height: int, *, lazy: bool) -> str:
    base = rel_path.rsplit(".", 1)[0]
    ext = rel_path.rsplit(".", 1)[-1]
    lazy_attr = ' loading="lazy"' if lazy else ""
    return (
        f"<picture>"
        f'<source srcset="{prefix}{base}.webp" type="image/webp">'
        f'<img src="{prefix}{rel_path}" alt="{alt}" width="{width}" height="{height}"'
        f'{lazy_attr} decoding="async">'
        f"</picture>"
    )


def patch_raster_images(html: str, path: Path) -> str:
    prefix = prefix_for(path)
    replacements = [
        (
            r'<img src="([^"]*assets/projects/telangana-stride-hub)\.jpg" alt="([^"]*)" width="(\d+)" height="(\d+)"([^>]*)>',
            "telangana-stride-hub.jpg",
        ),
        (
            r'<img src="([^"]*assets/projects/unstop-seo-audit)\.png" alt="([^"]*)" width="(\d+)" height="(\d+)"([^>]*)>',
            "unstop-seo-audit.png",
        ),
        (
            r'<img src="([^"]*assets/projects/lighthouse-global-scores-proof)\.png" alt="([^"]*)" width="(\d+)" height="(\d+)"([^>]*)>',
            "lighthouse-global-scores-proof.png",
        ),
        (
            r'<img src="([^"]*assets/projects/100hires)\.png" alt="([^"]*)" width="(\d+)" height="(\d+)"([^>]*)>',
            "100hires.png",
        ),
        (
            r'<img([^>]*)src="([^"]*assets/profile/faiz-headshot)\.png"([^>]*)>',
            "faiz-headshot.png",
        ),
    ]

    def repl_project(match: re.Match[str], filename: str) -> str:
        src_prefix = match.group(1).split("assets")[0]
        alt = match.group(2)
        w, h = match.group(3), match.group(4)
        lazy = "loading=" not in match.group(5) or 'loading="lazy"' in match.group(5)
        folder = "assets/profile" if filename == "faiz-headshot.png" else "assets/projects"
        return picture_img(src_prefix, f"{folder}/{filename}", alt, int(w), int(h), lazy=lazy)

    for pattern, filename in replacements[:4]:
        html = re.sub(
            pattern,
            lambda m, f=filename: repl_project(m, f.split("/")[-1]),
            html,
        )

    def repl_headshot(m: re.Match[str]) -> str:
        before, src_core, after = m.group(1), m.group(2), m.group(3)
        alt_m = re.search(r'alt="([^"]*)"', before + after)
        alt = alt_m.group(1) if alt_m else "Mohd Faizuddin Ahmed headshot"
        w_m = re.search(r'width="(\d+)"', before + after)
        h_m = re.search(r'height="(\d+)"', before + after)
        w = int(w_m.group(1)) if w_m else 360
        h = int(h_m.group(1)) if h_m else 360
        src_prefix = src_core.split("assets")[0]
        return picture_img(src_prefix, "assets/profile/faiz-headshot.png", alt, w, h, lazy=True)

    html = re.sub(
        r'<img([^>]*)src="([^"]*assets/profile/faiz-headshot)\.png"([^>]*)>',
        repl_headshot,
        html,
    )
    return html


def remove_font_import_from_css() -> None:
    css_path = ROOT / "assets" / "css" / "site.css"
    text = css_path.read_text(encoding="utf-8")
    text = re.sub(
        r'@import url\("https://fonts\.googleapis\.com/css2\?[^"]+"\);\s*',
        "",
        text,
        count=1,
    )
    css_path.write_text(text, encoding="utf-8")
    print("removed font @import from site.css")


def add_picture_css() -> None:
    css_path = ROOT / "assets" / "css" / "site.css"
    text = css_path.read_text(encoding="utf-8")
    if ".brand picture" in text:
        return
    insert = """
.brand picture {
  display: contents;
}

.proof-card__media picture,
.profile-headshot picture {
  display: block;
  width: 100%;
  height: 100%;
}

.proof-card__media picture img,
.profile-headshot picture img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
"""
    text = text.replace(".brand-logo--light,", insert + "\n.brand-logo--light,", 1)
    css_path.write_text(text, encoding="utf-8")
    print("added picture CSS rules")


def patch_html_files() -> None:
    for path in ROOT.rglob("*.html"):
        if path in SKIP or "node_modules" in path.parts:
            continue
        original = path.read_text(encoding="utf-8")
        updated = patch_head(original, path)
        updated = patch_brand(updated, path)
        updated = patch_raster_images(updated, path)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            print(f"patched {path.relative_to(ROOT)}")


def main() -> None:
    optimize_images()
    remove_font_import_from_css()
    add_picture_css()
    patch_html_files()
    print("Performance optimization complete.")


if __name__ == "__main__":
    main()
