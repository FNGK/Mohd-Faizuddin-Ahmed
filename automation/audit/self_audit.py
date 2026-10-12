#!/usr/bin/env python3
"""Self-audit engine for the SEO With Faiz marketing team — the EVIDENCE layer.

This is the deterministic half of the daily self-audit. It only reports a
finding when it can attach a concrete, observed piece of evidence (a file, a
line, a date, a count, a hash). A check that cannot gather evidence returns
`skipped` — never a finding. That is the anti-fabrication gate: the system is
structurally unable to invent a "loophole" to look busy. The judgment half
(the daily Claude routine) reasons ON TOP of this floor against the Neil-Patel
quality bar; it must not raise a finding this engine could have proven but did
not.

Every finding carries a confidence:
  CONFIRMED  — the evidence is unambiguous (a price string, a banned phrase, a
               real date gap, a duplicate file hash).
  PLAUSIBLE  — the evidence is real but the judgment is heuristic (e.g. "only
               1 internal link" might be fine for a short post).

Exit code is ALWAYS 0 — this is an audit, not CI; a clean run (zero findings)
is a valid and expected outcome, logged as "within standard".

Checks (all read-only):
  1. cadence        — days since last shipped piece per channel (LOG.md)
  2. queue_depth    — count of live (unused, non-paused) angles (QUEUE.md)
  3. banned_phrases — AI-tell / discount / begging language in copy
  4. prices         — any $/₹/Rs amount (the "no prices ever" rule)
  5. forbidden_link — direct buttoneyes.in links (must link the case study)
  6. internal_links — blog posts with < 2 links to owned service/case pages
  7. image_dupes    — identical social images (enforces "no two alike")
  8. metrics_fresh  — METRICS.md staleness (6-month memory must be current)
  9. self_integrity — scripts/dirs the skill depends on actually exist (META)

Usage:
  python automation/audit/self_audit.py            # writes marketing/audit/*
  python automation/audit/self_audit.py --quiet     # only the summary line
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MARKETING = ROOT / "marketing"
AUDIT_DIR = MARKETING / "audit"

TODAY = date.today()

# --- standards (the objective floor; the rubric bar lives in the skill) ------
CADENCE_MAX_DAYS = 3          # a channel silent longer than this is a gap
QUEUE_MIN_LIVE = 10           # strategist keeps >=10 angles ready
INTERNAL_LINK_MIN = 2         # blog posts link >=2 owned pages
METRICS_MAX_STALE_DAYS = 8    # METRICS.md updated at least weekly

# HARD bans: AI-tells / begging that are almost never legitimate -> CONFIRMED.
BANNED_HARD = [
    "delve", "seamless", "elevate your", "game-changer", "game changer",
    "in today's digital landscape", "look no further", "cutting-edge",
    "best-in-class", "limited offer", "limited time",
    "link in bio", "please follow", "please like", "please share",
]
# SOFT bans: words with legitimate critical/technical uses ("high-leverage",
# "cheap hosting is slow", "it's cheap to add"). Context decides, so these are
# PLAUSIBLE with a snippet for the judgment layer to adjudicate -- the engine
# must not hard-fail good writing on a bare substring.
BANNED_SOFT = ["leverage", "unlock", "cheap", "affordable", "budget-friendly"]
# A price is a currency symbol + a NON-ZERO amount. "$0" is rhetorical, not a
# rate card, so it is excluded.
PRICE_RE = re.compile(r"(?<![\w])(?:\$|₹|Rs\.?\s?|INR\s?|USD\s?)\s?(\d[\d,]*(?:\.\d+)?)\b", re.I)
DATE_RE = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")
FORBIDDEN_LINK_RE = re.compile(r"https?://(?:www\.)?buttoneyes\.in", re.I)
INTERNAL_LINK_RE = re.compile(r'href=["\'][^"\']*/(services|case-studies)/[^"\']*["\']', re.I)


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(p)


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


class Report:
    def __init__(self):
        self.findings: list[dict] = []
        self.skipped: list[dict] = []
        self.checks_run = 0

    def finding(self, check, severity, confidence, summary, evidence, fix):
        self.findings.append({
            "check": check, "severity": severity, "confidence": confidence,
            "summary": summary, "evidence": evidence, "suggested_fix": fix,
        })

    def skip(self, check, reason):
        self.skipped.append({"check": check, "reason": reason})


# --- helpers ----------------------------------------------------------------

def latest_date_in(text: str):
    found = [date(int(y), int(m), int(d)) for y, m, d in DATE_RE.findall(text)
             if 1 <= int(m) <= 12 and 1 <= int(d) <= 31]
    return max(found) if found else None


def published_copy():
    """Files whose text becomes PUBLIC. Brand/voice/price rules apply here.
    Internal planning docs (STRATEGY/METRICS/LOG/PROSPECTS) are deliberately
    excluded — they legitimately discuss retainer targets and critique words."""
    out = []
    for sub in ("blog/drafts", "blog/posts"):
        d = ROOT / sub
        if d.exists():
            out += sorted(d.glob("*.md")) + sorted(d.glob("*.html"))
    return out


def live_queue_quotes():
    """The quoted angle text of LIVE (unused, non-paused) queue items only —
    this is copy that will actually go out. Used/struck (~~) and PAUSED angles
    are skipped so the audit never flags retired copy."""
    q = MARKETING / "QUEUE.md"
    items = []
    if not q.exists():
        return items
    for i, ln in enumerate(read(q).splitlines(), 1):
        s = ln.strip()
        if not s.startswith("- ") or "~~" in ln or "PAUSED" in ln:
            continue
        m = re.search(r'"([^"]+)"', ln)
        if m:
            items.append((m.group(1), i))
    return items


def scan_surfaces():
    """(display, text, fixed_line) over everything that becomes outbound copy.
    fixed_line is set for one-line queue quotes; None means derive from offset."""
    surfaces = [(rel(f), read(f), None) for f in published_copy()]
    for quote, line in live_queue_quotes():
        surfaces.append((f"marketing/QUEUE.md:{line} (live angle)", quote, line))
    return surfaces


def snippet(text, idx, span=52):
    a, b = max(0, idx - span), min(len(text), idx + span)
    return text[a:b].replace("\n", " ").strip()


def line_of(text, idx, fixed):
    return fixed if fixed is not None else text[:idx].count("\n") + 1


# --- checks -----------------------------------------------------------------

def check_cadence(r: Report):
    r.checks_run += 1
    log = MARKETING / "LOG.md"
    if not log.exists():
        return r.skip("cadence", "marketing/LOG.md not found")
    last = latest_date_in(read(log))
    if not last:
        return r.skip("cadence", "no dated entries in LOG.md")
    gap = (TODAY - last).days
    if gap > CADENCE_MAX_DAYS:
        r.finding("cadence", "high", "CONFIRMED",
                  f"No shipped piece logged in {gap} days (last {last.isoformat()}).",
                  {"last_shipped": last.isoformat(), "days_idle": gap,
                   "threshold": CADENCE_MAX_DAYS, "source": "marketing/LOG.md"},
                  "Schedule the next queued angle today; investigate why the routine stopped logging.")


def check_queue_depth(r: Report):
    r.checks_run += 1
    q = MARKETING / "QUEUE.md"
    if not q.exists():
        return r.skip("queue_depth", "marketing/QUEUE.md not found")
    live = 0
    for ln in read(q).splitlines():
        s = ln.strip()
        if not s.startswith("- "):
            continue
        if s.startswith("- ~~") or "~~" in s[:6]:   # struck-through = used
            continue
        if "PAUSED" in ln:
            continue
        live += 1
    if live < QUEUE_MIN_LIVE:
        r.finding("queue_depth", "medium", "CONFIRMED",
                  f"Only {live} live angles in the queue (target >= {QUEUE_MIN_LIVE}).",
                  {"live_angles": live, "threshold": QUEUE_MIN_LIVE,
                   "source": "marketing/QUEUE.md"},
                  "Strategist refill: add fresh angles anchored to live pages before the queue dries up.")


def check_banned_and_prices(r: Report):
    r.checks_run += 3  # hard-banned + soft-banned + prices (+ forbidden link)
    hard_hits, soft_hits, price_hits, link_hits = [], [], [], []
    surfaces = scan_surfaces()
    hard_res = [(p, re.compile(r"(?<![\w-])" + re.escape(p) + r"(?![\w-])", re.I))
                for p in BANNED_HARD]
    soft_res = [(w, re.compile(r"(?<![\w-])" + re.escape(w) + r"(?![\w-])", re.I))
                for w in BANNED_SOFT]
    for disp, txt, fixed in surfaces:
        for phrase, rx in hard_res:
            for m in rx.finditer(txt):
                hard_hits.append({"where": disp, "line": line_of(txt, m.start(), fixed),
                                  "phrase": phrase, "snippet": snippet(txt, m.start())})
        for word, rx in soft_res:
            for m in rx.finditer(txt):
                soft_hits.append({"where": disp, "line": line_of(txt, m.start(), fixed),
                                  "word": word, "snippet": snippet(txt, m.start())})
        for m in PRICE_RE.finditer(txt):
            amount = m.group(1).replace(",", "")
            try:
                if float(amount) == 0:      # "$0" is rhetorical, not a rate card
                    continue
            except ValueError:
                pass
            price_hits.append({"where": disp, "line": line_of(txt, m.start(), fixed),
                               "match": m.group(0).strip(), "snippet": snippet(txt, m.start())})
        for m in FORBIDDEN_LINK_RE.finditer(txt):
            link_hits.append({"where": disp, "line": line_of(txt, m.start(), fixed),
                              "match": m.group(0)})

    if hard_hits:
        r.finding("banned_phrases", "medium", "CONFIRMED",
                  f"{len(hard_hits)} hard-banned phrase(s) in outbound copy.",
                  {"hits": hard_hits[:25], "total": len(hard_hits)},
                  "Rewrite each flagged line in Faiz's voice (banned list in the skill non-negotiables).")
    if soft_hits:
        r.finding("voice_watchlist", "low", "PLAUSIBLE",
                  f"{len(soft_hits)} context-dependent word(s) to eyeball (may be legitimate).",
                  {"hits": soft_hits[:25], "total": len(soft_hits),
                   "note": "e.g. 'high-leverage' or 'cheap hosting is slow' are fine; "
                           "only self-positioning uses ('we're affordable') fail."},
                  "Judgment layer: read each snippet; rewrite only genuine AI-tells/discount positioning.")
    if price_hits:
        r.finding("prices", "high", "CONFIRMED",
                  f"{len(price_hits)} non-zero price string(s) in outbound copy ('no prices ever').",
                  {"hits": price_hits[:25], "total": len(price_hits)},
                  "Remove the amount; convey premium via tone. Confirm each snippet is a rate, not a cited stat.")
    if link_hits:
        r.finding("forbidden_link", "high", "CONFIRMED",
                  f"{len(link_hits)} direct buttoneyes.in link(s) in outbound copy.",
                  {"hits": link_hits[:25], "total": len(link_hits)},
                  "Replace with /case-studies/button-eyes-resort.html.")


def check_internal_links(r: Report):
    r.checks_run += 1
    posts = sorted((ROOT / "blog" / "posts").glob("*.html")) if (ROOT / "blog" / "posts").exists() else []
    if not posts:
        return r.skip("internal_links", "no blog/posts/*.html")
    thin = []
    for p in posts:
        n = len(set(INTERNAL_LINK_RE.findall(read(p))))
        # findall returns the captured group only; recount full matches:
        n = len(INTERNAL_LINK_RE.findall(read(p)))
        if n < INTERNAL_LINK_MIN:
            thin.append({"file": rel(p), "internal_links": n})
    if thin:
        r.finding("internal_links", "low", "PLAUSIBLE",
                  f"{len(thin)} post(s) link < {INTERNAL_LINK_MIN} owned service/case pages.",
                  {"posts": thin[:25], "threshold": INTERNAL_LINK_MIN},
                  "Add contextual links to 2-3 relevant service/case pages (compounding check). Confirm each post's length warrants it before editing.")


def check_image_dupes(r: Report):
    r.checks_run += 1
    social = ROOT / "assets" / "social"
    if not social.exists():
        return r.skip("image_dupes", "assets/social not found")
    seen: dict[str, str] = {}
    dupes = []
    for img in list(social.rglob("*.png")) + list(social.rglob("*.jpg")):
        if "brand" in img.parts:        # the fixed logo mark is meant to repeat
            continue
        try:
            h = hashlib.sha1(img.read_bytes()).hexdigest()
        except Exception:
            continue
        if h in seen:
            dupes.append({"file": rel(img), "duplicate_of": seen[h]})
        else:
            seen[h] = rel(img)
    if dupes:
        r.finding("image_dupes", "medium", "CONFIRMED",
                  f"{len(dupes)} byte-identical social image(s) ('no two alike' rule).",
                  {"dupes": dupes[:25], "total": len(dupes)},
                  "Each post needs a freshly generated image; remove/replace the reused file.")


def check_metrics_fresh(r: Report):
    r.checks_run += 1
    m = MARKETING / "METRICS.md"
    if not m.exists():
        return r.skip("metrics_fresh", "marketing/METRICS.md not found")
    last = latest_date_in(read(m))
    if not last:
        return r.skip("metrics_fresh", "no dated rows in METRICS.md")
    stale = (TODAY - last).days
    if stale > METRICS_MAX_STALE_DAYS:
        r.finding("metrics_fresh", "medium", "PLAUSIBLE",
                  f"METRICS.md last updated {stale} days ago ({last.isoformat()}).",
                  {"last_row": last.isoformat(), "days_stale": stale,
                   "threshold": METRICS_MAX_STALE_DAYS, "source": "marketing/METRICS.md"},
                  "Growth Strategist: pull GA4 + Buffer/Meta this week and append a row (never delete rows).")


def check_self_integrity(r: Report):
    r.checks_run += 1
    required = [
        "automation/social/make_social_image.py",
        "automation/social/make_carousel.py",
        "automation/social/make_card.py",
        "assets/social/brand/icon-mark.png",
        "marketing/STRATEGY.md",
        "marketing/QUEUE.md",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    if missing:
        r.finding("self_integrity", "high", "CONFIRMED",
                  f"{len(missing)} dependency the system relies on is missing.",
                  {"missing": missing},
                  "Restore/create the missing file, or correct the skill reference that points to it.")


CHECKS = [check_cadence, check_queue_depth, check_banned_and_prices,
          check_internal_links, check_image_dupes, check_metrics_fresh,
          check_self_integrity]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    r = Report()
    for chk in CHECKS:
        try:
            chk(r)
        except Exception as e:   # a broken check must not fabricate or crash the audit
            r.skip(chk.__name__, f"check errored: {type(e).__name__}: {e}")

    sev_rank = {"high": 0, "medium": 1, "low": 2}
    r.findings.sort(key=lambda f: (sev_rank.get(f["severity"], 9), f["check"]))

    verdict = "within_standard" if not r.findings else "action_required"
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "verdict": verdict,
        "checks_run": r.checks_run,
        "findings_count": len(r.findings),
        "findings": r.findings,
        "skipped": r.skipped,
    }

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    (AUDIT_DIR / "latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (AUDIT_DIR / "latest.md").write_text(render_md(payload), encoding="utf-8")
    logline = (f"- {TODAY.isoformat()} — {verdict} — "
               f"{len(r.findings)} finding(s), {len(r.skipped)} skipped, "
               f"{r.checks_run} checks\n")
    with (AUDIT_DIR / "AUDIT-LOG.md").open("a", encoding="utf-8") as fh:
        fh.write(logline)

    print(f"[self-audit] {verdict.upper()} — {len(r.findings)} finding(s), "
          f"{len(r.skipped)} skipped, {r.checks_run} checks run")
    if not a.quiet:
        for f in r.findings:
            print(f"  [{f['severity']:^6}] {f['confidence']:<9} {f['check']}: {f['summary']}")
        if r.skipped:
            print(f"  (skipped: {', '.join(s['check'] for s in r.skipped)})")
    return 0


def render_md(p: dict) -> str:
    lines = [f"# Self-audit — {p['generated_at']}",
             "",
             f"**Verdict:** {p['verdict']}  |  "
             f"**Findings:** {p['findings_count']}  |  "
             f"**Checks run:** {p['checks_run']}  |  "
             f"**Skipped:** {len(p['skipped'])}",
             ""]
    if not p["findings"]:
        lines += ["_No evidence-backed findings. System within standard on the objective floor._",
                  "", "> The judgment-layer audit (Neil-Patel bar) still runs on top of this.", ""]
    else:
        lines.append("## Findings (evidence-backed, most severe first)\n")
        for i, f in enumerate(p["findings"], 1):
            lines += [f"### {i}. [{f['severity']}/{f['confidence']}] {f['check']}",
                      f"{f['summary']}", "",
                      f"- **Evidence:** `{json.dumps(f['evidence'], ensure_ascii=False)}`",
                      f"- **Suggested fix:** {f['suggested_fix']}", ""]
    if p["skipped"]:
        lines.append("## Skipped checks (no evidence available — NOT findings)\n")
        for s in p["skipped"]:
            lines.append(f"- `{s['check']}` — {s['reason']}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
