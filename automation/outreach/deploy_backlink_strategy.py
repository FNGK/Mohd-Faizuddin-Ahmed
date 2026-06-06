#!/usr/bin/env python3
"""Deploy and launch the SEO With Faiz off-page authority strategy."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTREACH_DIR = REPO_ROOT / "outreach"
MEASUREMENT_DIR = REPO_ROOT / "measurement"
OUTPUT_DIR = REPO_ROOT / "outreach" / "output" / "wave-1"

ANCHOR_URLS = [
    "https://seowithfaiz.com/resources/international-seo-diagnostic-framework.html",
    "https://seowithfaiz.com/resources/hreflang-market-rollout-checklist.html",
    "https://seowithfaiz.com/resources/international-seo-failure-patterns-us-companies.html",
    "https://seowithfaiz.com/resources/international-seo-expert-media-kit.html",
    "https://seowithfaiz.com/services/international-seo.html",
    "https://seowithfaiz.com/mentions.html",
]

EXPERT_QUOTE_TARGETS = {"Qwoted", "Featured", "SourceBottle"}
DIRECTORY_TARGETS = {"Clutch", "UpCity", "GoodFirms", "DesignRush"}

PITCH_TEMPLATES = {
    "editorial": """Subject: Source for international SEO / localization commentary

Hi {{name}},

I help US and cross-border companies diagnose international SEO expansion problems before they turn into hreflang debt, weak localization, and authority gaps.

If you ever need a source on:
- why same-language markets still need localization
- what hreflang does not fix
- how US teams should prioritize markets before rollout
- why international SEO needs market-level reporting

I can provide a concise expert quote quickly.

Useful references:
- Diagnostic framework: https://seowithfaiz.com/resources/international-seo-diagnostic-framework.html
- Media kit: https://seowithfaiz.com/resources/international-seo-expert-media-kit.html

Best,
Faiz
SEO With Faiz | https://seowithfaiz.com/
""",
    "podcast": """Subject: Guest idea - international SEO for US companies expanding abroad

Hi {{host}},

I work on international SEO and technical SEO for US and cross-border teams. A conversation that could fit your audience:

- Why international SEO failures usually start before hreflang
- How to choose the first serious market instead of expanding everywhere
- What localization mistakes hurt both rankings and conversions

Supporting resources:
- Framework: https://seowithfaiz.com/resources/international-seo-diagnostic-framework.html
- Failure patterns: https://seowithfaiz.com/resources/international-seo-failure-patterns-us-companies.html
- Media kit: https://seowithfaiz.com/resources/international-seo-expert-media-kit.html

Best,
Faiz
""",
    "directory": """Profile setup notes for {{target}}

Positioning:
- Independent international SEO and technical SEO consultant
- Remote delivery for US and cross-border companies
- Proof-first: public diagnostic framework, media kit, and case-linked resources

Primary URL: https://seowithfaiz.com/
Service page: https://seowithfaiz.com/services/international-seo.html
Media kit: https://seowithfaiz.com/resources/international-seo-expert-media-kit.html
LinkedIn: https://www.linkedin.com/in/seowithfaiz

Do not claim a US office or guaranteed rankings.
""",
    "partner": """Subject: Joint resource idea for localization / international growth teams

Hi {{partner}},

I help US and cross-border companies with international SEO, hreflang governance, and market rollout planning.

Your audience already cares about localization and global growth, so I think there is strong overlap for a co-created resource on:

- localization versus translation for SEO
- hreflang launch QA
- how teams should sequence market rollout and proof building

Useful references:
- Rollout checklist: https://seowithfaiz.com/resources/hreflang-market-rollout-checklist.html
- Diagnostic framework: https://seowithfaiz.com/resources/international-seo-diagnostic-framework.html

Best,
Faiz
""",
}


def check_url(url: str, timeout: int = 20) -> tuple[int | None, str | None]:
    request = urllib.request.Request(url, method="HEAD")
    request.add_header("User-Agent", "SEOWithFaiz-DeployBot/1.0")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, None
    except urllib.error.HTTPError as exc:
        if exc.code in {403, 405}:
            return check_url_get(url, timeout)
        return exc.code, str(exc)
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def check_url_get(url: str, timeout: int = 20) -> tuple[int | None, str | None]:
    request = urllib.request.Request(url, method="GET")
    request.add_header("User-Agent", "SEOWithFaiz-DeployBot/1.0")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, None
    except urllib.error.HTTPError as exc:
        return exc.code, str(exc)
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def validate_assets() -> int:
    failures = 0
    print("Anchor asset check:")
    for url in ANCHOR_URLS:
        status, error = check_url(url)
        if status == 200:
            print(f"  OK  {url}")
        else:
            failures += 1
            detail = error or f"HTTP {status}"
            print(f"  FAIL {url} ({detail})")
    return failures


def load_targets() -> list[dict[str, str]]:
    path = OUTREACH_DIR / "us-international-seo-authority-targets.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def wave_for_row(row: dict[str, str]) -> str:
    category = row["category"]
    target = row["target"]
    if category == "editorial" and target in EXPERT_QUOTE_TARGETS:
        return "wave-1-expert-platforms"
    if category == "directory" and target in DIRECTORY_TARGETS:
        return "wave-1-directories"
    if category == "podcast" and row["priority"] == "1":
        return "wave-2-podcasts"
    if category == "partner" and row["priority"] == "1":
        return "wave-3-partners"
    return "wave-4-long-tail"


def generate_wave1() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    queue_path = OUTPUT_DIR / "wave-1-queue.csv"
    rows: list[dict[str, str]] = []

    for row in load_targets():
        wave = wave_for_row(row)
        if not wave.startswith("wave-1"):
            continue
        pitch_type = row["category"]
        template = PITCH_TEMPLATES.get(pitch_type, PITCH_TEMPLATES["editorial"])
        pitch = template.replace("{{target}}", row["target"]).replace("{{partner}}", row["target"])
        slug = row["target"].lower().replace(" ", "-").replace("/", "-")
        pitch_path = OUTPUT_DIR / f"{slug}.txt"
        pitch_path.write_text(pitch, encoding="utf-8")
        rows.append(
            {
                "wave": wave,
                "priority": row["priority"],
                "category": row["category"],
                "target": row["target"],
                "site_url": row["site_url"],
                "initial_angle": row["initial_angle"],
                "pitch_file": str(pitch_path.relative_to(REPO_ROOT)).replace("\\", "/"),
                "status": "queued",
                "notes": "",
            }
        )

    with queue_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "wave",
                "priority",
                "category",
                "target",
                "site_url",
                "initial_angle",
                "pitch_file",
                "status",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    manifest = {
        "generated_on": date.today().isoformat(),
        "queue_csv": str(queue_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "pitch_count": len(rows),
        "waves": {
            "wave-1-expert-platforms": sum(1 for r in rows if r["wave"] == "wave-1-expert-platforms"),
            "wave-1-directories": sum(1 for r in rows if r["wave"] == "wave-1-directories"),
        },
    }
    (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Generated {len(rows)} wave-1 pitches in {OUTPUT_DIR}")
    return queue_path


def print_plan() -> None:
    print("SEO With Faiz off-page deployment plan")
    print("1. Validate anchor assets are live on seowithfaiz.com")
    print("2. Register expert-source profiles: Qwoted, Featured, SourceBottle")
    print("3. Submit directory profiles: Clutch, UpCity, GoodFirms, DesignRush")
    print("4. Send podcast pitches only after expert-platform profiles are live")
    print("5. Log every live mention in mentions.html and off-page-authority-tracker.csv")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true", help="Check live anchor URLs")
    parser.add_argument("--generate-wave1", action="store_true", help="Build wave-1 pitch queue")
    parser.add_argument("--plan", action="store_true", help="Print deployment sequence")
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        return 0

    exit_code = 0
    if args.plan:
        print_plan()
    if args.validate:
        exit_code = validate_assets()
    if args.generate_wave1:
        generate_wave1()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
