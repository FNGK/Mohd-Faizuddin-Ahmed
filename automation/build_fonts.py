"""Build the self-hosted brand fonts in assets/fonts/ (SIL Open Font License).

Downloads the variable fonts from the Google Fonts CSS API, keeps the latin and
latin-ext character sets, and trims each file to what the site uses:
  - axis ranges: Fraunces weight 500-800 and optical size 9-72 (the largest
    Fraunces text is 64px), Hanken Grotesk weight 400-800, JetBrains Mono
    weight 400-500 (mono is only used for small labels);
  - layout features: keeps kerning, ligatures and mark positioning, drops code
    ligatures (calt) and fraction features the site never uses.
Output ~31% smaller than Google's files with identical rendering in range.
Prints the @font-face rules for assets/css/site.css.

Requires: pip install fonttools brotli
Usage:    python automation/build_fonts.py
"""
import io
import pathlib
import re
import urllib.request

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "fonts"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
API = ("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500..800"
       "&family=Hanken+Grotesk:wght@400..800&family=JetBrains+Mono:wght@400..700&display=swap")
FAMILIES = {
    "Fraunces": {"slug": "fraunces", "limits": {"wght": (500, 800), "opsz": (9, 72)}, "weight": "500 800"},
    "Hanken Grotesk": {"slug": "hanken-grotesk", "limits": {"wght": (400, 800)}, "weight": "400 800"},
    "JetBrains Mono": {"slug": "jetbrains-mono", "limits": {"wght": (400, 500)}, "weight": "400 500"},
}
SUBSETS = ("latin-ext", "latin")
FEATURES = ["kern", "liga", "ccmp", "locl", "mark", "mkmk", "rvrn", "case"]


def unicodes(spec):
    out = []
    for part in spec.split(","):
        a, _, b = part.strip().replace("U+", "").partition("-")
        out.extend(range(int(a, 16), int(b or a, 16) + 1))
    return out


def trim(data, limits, unicode_range):
    font = TTFont(io.BytesIO(data), lazy=False)
    font = instancer.instantiateVariableFont(font, limits)
    buf = io.BytesIO()
    font.save(buf)  # round-trip so the variation tables are rebuilt before subsetting
    font = TTFont(io.BytesIO(buf.getvalue()), lazy=False)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = FEATURES
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    subsetter = subset.Subsetter(opts)
    subsetter.populate(unicodes=unicodes(unicode_range))
    subsetter.subset(font)
    font.flavor = "woff2"
    out = io.BytesIO()
    font.save(out)
    return out.getvalue()


def main():
    css = urllib.request.urlopen(urllib.request.Request(API, headers={"User-Agent": UA}), timeout=30).read().decode()
    rules = []
    for subset_name, body in re.findall(r"/\*\s*([\w-]+)\s*\*/\s*@font-face\s*\{(.*?)\}", css, re.S):
        if subset_name not in SUBSETS:
            continue
        family = re.search(r"font-family:\s*'([^']+)'", body).group(1)
        spec = FAMILIES[family]
        url = re.search(r"url\(([^)]+)\)", body).group(1)
        urange = re.search(r"unicode-range:\s*([^;]+);", body).group(1).strip()
        original = urllib.request.urlopen(url, timeout=30).read()
        data = trim(original, spec["limits"], urange)
        name = f"{spec['slug']}-{subset_name}.woff2"
        (OUT / name).write_bytes(data)
        print(f"/* {name}: {len(original) / 1024:.1f} KB -> {len(data) / 1024:.1f} KB */")
        rules.append(
            f'@font-face {{ font-family: "{family}"; font-style: normal; font-weight: {spec["weight"]}; font-display: swap; '
            f'src: url("../fonts/{name}") format("woff2"); unicode-range: {urange}; }}'
        )
    print("\n".join(rules))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    main()
