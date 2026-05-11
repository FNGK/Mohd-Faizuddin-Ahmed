"""Insert absolute favicon link after viewport meta (once per file)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER = '<link rel="icon"'
LINK = (
    '  <link rel="icon" href="https://seowithfaiz.com/assets/logos/seowithfaiz-icon.svg" '
    'type="image/svg+xml">\n'
)


def main() -> None:
    for path in ROOT.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            continue
        needle = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        if needle not in text:
            continue
        text = text.replace(
            needle,
            needle + "\n" + LINK,
            1,
        )
        path.write_text(text, encoding="utf-8")
        print("favicon", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
