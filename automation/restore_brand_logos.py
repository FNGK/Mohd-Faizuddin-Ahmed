#!/usr/bin/env python3
"""Restore original brand logo markup and assets across all marketing pages."""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SKIP = {
    ROOT / "Professional_Resume.html",
    ROOT / "automation" / "blog" / "admin" / "review.html",
}

LOGO_LIGHT = "seo-with-faiz-logo-technical-precision-revenue-growth.png"
LOGO_DARK = "seo-with-faiz-logo-dark-mode-technical-precision-revenue-growth.png"
ALT_LIGHT = (
    "SEO With Faiz logo — technical SEO and revenue growth services; shield mark with "
    "code, bridge, and growth chart (transparent PNG for light mode)."
)

HEADER_DERIVATIVES = [
    "seo-with-faiz-logo-header.png",
    "seo-with-faiz-logo-header.webp",
    "seo-with-faiz-logo-dark-header.png",
    "seo-with-faiz-logo-dark-header.webp",
]


def prefix_for(path: Path) -> str:
    depth = len(path.relative_to(ROOT).parts) - 1
    return "./" if depth == 0 else "../" * depth


def brand_markup(prefix: str, *, high_priority: bool) -> str:
    prio = ' fetchpriority="high"' if high_priority else ""
    return (
        f'      <a class="brand" href="{prefix}index.html" aria-label="SEO With Faiz home">\n'
        f'        <img class="brand-logo brand-logo--light" src="{prefix}assets/logos/{LOGO_LIGHT}" '
        f'alt="{ALT_LIGHT}" width="1024" height="498" decoding="async"{prio}>\n'
        f'        <img class="brand-logo brand-logo--dark" src="{prefix}assets/logos/{LOGO_DARK}" alt="" '
        f'width="580" height="228" decoding="async" aria-hidden="true">\n'
        f"      </a>"
    )


def patch_brand(html: str, path: Path) -> str:
    prefix = prefix_for(path)
    high = path.name == "index.html" and path.parent == ROOT
    block = brand_markup(prefix, high_priority=high)
    pattern = re.compile(
        r'<a class="brand" href="[^"]*" aria-label="SEO With Faiz home">[\s\S]*?</a>',
        re.DOTALL,
    )
    return pattern.sub(block, html, count=1)


def patch_preload(html: str, path: Path) -> str:
    if path.name != "index.html" or path.parent != ROOT:
        return html
    prefix = prefix_for(path)
    logo_preload = (
        f'  <link rel="preload" as="image" href="{prefix}assets/logos/{LOGO_LIGHT}">\n'
    )
    html = re.sub(
        r'\s*<link rel="preload" as="image" href="[^"]*seo-with-faiz-logo-header\.webp"[^>]*>\n?',
        "",
        html,
    )
    needle = '<link rel="preload" as="style" href="https://fonts.googleapis.com'
    if logo_preload.strip() not in html and needle in html:
        html = html.replace(needle, logo_preload + "  " + needle, 1)
    return html


def write_lossless_webp(png_path: Path) -> None:
    """Optional full-size WebP for future use; not referenced in HTML (PNG stays canonical)."""
    out = png_path.with_suffix(".webp")
    img = Image.open(png_path)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    img.save(out, "WEBP", quality=95, method=6, lossless=False)
    print(f"webp {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")


def remove_header_derivatives() -> None:
    logos = ROOT / "assets" / "logos"
    for name in HEADER_DERIVATIVES:
        path = logos / name
        if path.exists():
            path.unlink()
            print(f"removed {path.relative_to(ROOT)}")


def main() -> None:
    remove_header_derivatives()
    logos = ROOT / "assets" / "logos"
    write_lossless_webp(logos / LOGO_LIGHT)
    write_lossless_webp(logos / LOGO_DARK)

    for path in ROOT.rglob("*.html"):
        if path in SKIP or "node_modules" in path.parts:
            continue
        original = path.read_text(encoding="utf-8")
        updated = patch_brand(original, path)
        updated = patch_preload(updated, path)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            print(f"restored {path.relative_to(ROOT)}")

    print("Brand logos restored to original assets.")


if __name__ == "__main__":
    main()
