"""Run on Windows (reads the system Georgia/Arial/Courier New files) and paste the
printed @font-face rules into assets/css/site.css.

Compute size-adjust / ascent / descent / line-gap overrides so a local system
font takes up the same space as each self-hosted web font. The web fonts are
variable, so each is measured at the weight it is mostly used at. Average width
is weighted by English letter frequency (the approach capsize/Next.js use)."""
import io, os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts")  # self-hosted woff2 files
WIN = "C:/Windows/Fonts/"
# English letter frequencies (per 1000) plus space.
FREQ = {"a": 82, "b": 15, "c": 28, "d": 43, "e": 127, "f": 22, "g": 20, "h": 61, "i": 70, "j": 2,
        "k": 8, "l": 40, "m": 24, "n": 67, "o": 75, "p": 19, "q": 1, "r": 60, "s": 63, "t": 91,
        "u": 28, "v": 10, "w": 24, "x": 2, "y": 20, "z": 1, " ": 180}

def load(path, axes=None):
    f = TTFont(path)
    if axes and "fvar" in f:
        supported = {a.axisTag: (a.minValue, a.maxValue) for a in f["fvar"].axes}
        loc = {k: min(max(v, supported[k][0]), supported[k][1]) for k, v in axes.items() if k in supported}
        f = instancer.instantiateVariableFont(f, loc)
    return f

def metrics(font):
    upm = font["head"].unitsPerEm
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    total = weight = 0
    for ch, freq in FREQ.items():
        g = cmap.get(ord(ch))
        if g:
            total += hmtx[g][0] * freq
            weight += freq
    os2, hhea = font["OS/2"], font["hhea"]
    use_typo = bool(os2.fsSelection & (1 << 7))
    asc, desc, gap = (os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap) if use_typo else (hhea.ascent, hhea.descent, hhea.lineGap)
    return {"upm": upm, "avg": total / weight / upm, "asc": asc / upm, "desc": abs(desc) / upm, "gap": gap / upm, "typo": use_typo}

def overrides(web, fallback):
    size = web["avg"] / fallback["avg"]
    return {"size-adjust": size * 100, "ascent-override": web["asc"] / size * 100,
            "descent-override": web["desc"] / size * 100, "line-gap-override": web["gap"] / size * 100}

PAIRS = [
    # family, web file, measured axes, fallback faces [(local names, file, weight range)]
    ("Fraunces", "fraunces-latin.woff2", {"wght": 700, "opsz": 72},
        [(["Georgia"], "georgia.ttf", "400 599"), (["Georgia Bold", "Georgia-Bold"], "georgiab.ttf", "600 900")]),
    ("Hanken Grotesk", "hanken-grotesk-latin.woff2", {"wght": 400},
        [(["Arial"], "arial.ttf", "400 599"), (["Arial Bold", "Arial-BoldMT"], "arialbd.ttf", "600 900")]),
    ("JetBrains Mono", "jetbrains-mono-latin.woff2", {"wght": 500},
        [(["Courier New"], "cour.ttf", "400 900")]),
]

css = []
for family, webfile, axes, fallbacks in PAIRS:
    web = metrics(load(os.path.join(HERE, webfile), axes))
    print(f"{family}: avg {web['avg']:.4f} asc {web['asc']:.3f} desc {web['desc']:.3f} gap {web['gap']:.3f} typo={web['typo']}")
    for names, fbfile, wrange in fallbacks:
        fb = metrics(load(WIN + fbfile))
        o = overrides(web, fb)
        print(f"   vs {names[0]:12s} avg {fb['avg']:.4f} -> size-adjust {o['size-adjust']:.2f}%")
        src = ", ".join(f'local("{n}")' for n in names)
        css.append(
            f'@font-face {{ font-family: "{family} Fallback"; src: {src}; font-weight: {wrange}; '
            f'size-adjust: {o["size-adjust"]:.2f}%; ascent-override: {o["ascent-override"]:.2f}%; '
            f'descent-override: {o["descent-override"]:.2f}%; line-gap-override: {o["line-gap-override"]:.2f}%; }}'
        )
print("\n" + "\n".join(css))
