#!/usr/bin/env python3
"""Put the head bootstrap inline at the top of every public page's <head>.

The bootstrap does two things before first paint:
  - applies the saved light/dark theme (dark by default), so there is no flash;
  - sends visitors of the GitHub Pages copy (fngk.github.io/Mohd-Faizuddin-Ahmed/…)
    to the same path on seowithfaiz.com.
It used to be assets/js/canonical-redirect.js, a render-blocking download on
every page. Inline it costs no request; the site's CSP allows exactly this
script through its sha256 hash, which this tool prints and checks in _headers.
Any change to BOOTSTRAP changes the hash: re-run this tool and update _headers.

It also removes 404.html's old inline redirect: the bootstrap covers GitHub
Pages 404s, and that script would reload the same URL forever on seowithfaiz.com
(it only ever stayed harmless because the CSP blocked it).

Usage: python automation/inject_head_bootstrap.py [--check]
"""

import base64
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {"cms", "automation", "node_modules", ".git", ".wrangler"}
SKIP_NAMES = {"formsubmit-test-out.html", "Professional_Resume.html", "mocktest.html"}

BOOTSTRAP = (
    '(function(){var d=document.documentElement;'
    'try{d.setAttribute("data-theme",localStorage.getItem("seowithfaiz-theme")||"dark")}'
    'catch(e){d.setAttribute("data-theme","dark")}'
    'var b="/Mohd-Faizuddin-Ahmed";'
    'if(location.hostname==="fngk.github.io"&&location.pathname.indexOf(b)===0){'
    'var p=location.pathname.slice(b.length)||"/";if(p.charAt(0)!=="/")p="/"+p;'
    'location.replace("https://seowithfaiz.com"+p+location.search+location.hash)}})();'
)
TAG = "<script>" + BOOTSTRAP + "</script>"
OLD_TAG = re.compile(r'<script src="[^"]*canonical-redirect\.js"></script>')
OLD_404_REDIRECT = re.compile(
    r'[ \t]*<script>\s*\(function \(\) \{\s*var base = \'https://seowithfaiz\.com\';.*?\}\)\(\);\s*</script>[ \t]*\r?\n',
    re.S,
)


def csp_hash() -> str:
    return "'sha256-" + base64.b64encode(hashlib.sha256(BOOTSTRAP.encode()).digest()).decode() + "'"


def public_pages():
    for html in ROOT.rglob("*.html"):
        rel = html.relative_to(ROOT)
        if SKIP_PARTS.intersection(rel.parts) or rel.name in SKIP_NAMES:
            continue
        yield html, rel


def main() -> int:
    check = "--check" in sys.argv
    changed, problems = 0, []
    for html, rel in public_pages():
        text = html.read_text(encoding="utf-8")
        # Only pages that already carry the bootstrap (old tag or inline). The CRM
        # and the standalone client pack have their own theming and never had it.
        if "canonical-redirect.js" not in text and TAG not in text:
            continue
        new = OLD_TAG.sub(TAG, text)
        new = OLD_404_REDIRECT.sub("", new)
        if new.count(TAG) != 1 or "canonical-redirect.js" in new:
            problems.append(str(rel))
        if new != text:
            changed += 1
            if not check:
                html.write_text(new, encoding="utf-8", newline="")
    headers = (ROOT / "_headers").read_text(encoding="utf-8")
    hash_ok = csp_hash() in headers
    print(f"{'would update' if check else 'updated'} {changed} pages; CSP hash {csp_hash()} "
          f"{'present' if hash_ok else 'MISSING'} in _headers")
    for p in problems:
        print("  needs attention:", p)
    return 0 if (hash_ok and not problems and (not check or changed == 0)) else 1


if __name__ == "__main__":
    sys.exit(main())
