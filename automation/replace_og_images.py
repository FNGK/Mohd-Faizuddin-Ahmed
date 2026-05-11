import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OG = "https://seowithfaiz.com/assets/og/og-default.png"


def main() -> None:
    for path in ROOT.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        out = re.sub(
            r'(<meta property="og:image" content=")[^"]+(")',
            rf"\1{OG}\2",
            text,
        )
        out = re.sub(
            r'(<meta name="twitter:image" content=")[^"]+(")',
            rf"\1{OG}\2",
            out,
        )
        if out != text:
            path.write_text(out, encoding="utf-8")
            print("updated", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
