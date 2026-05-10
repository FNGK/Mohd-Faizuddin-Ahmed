#!/usr/bin/env python3
"""
Insert signal-board figure + section-band (visual strip) into static HTML pages.
Run from repo root: python automation/patch_signal_visual_all.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def figure_block(gid: str) -> str:
    return f"""          <figure class="signal-board">
            <div class="signal-board__top">
              <span class="signal-board__title">Organic sessions</span>
              <span class="signal-board__pill">Illustrative</span>
            </div>
            <svg viewBox="0 0 320 118" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <defs>
                <linearGradient id="{gid}" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stop-color="var(--primary)" stop-opacity="0.38" />
                  <stop offset="100%" stop-color="var(--primary)" stop-opacity="0" />
                </linearGradient>
              </defs>
              <g opacity="0.55" stroke="var(--border)" stroke-width="0.75">
                <line x1="0" y1="28" x2="320" y2="28" />
                <line x1="0" y1="56" x2="320" y2="56" />
                <line x1="0" y1="84" x2="320" y2="84" />
              </g>
              <path
                d="M0 96 L42 90 L84 74 L126 80 L168 62 L210 54 L252 44 L294 36 L320 26 L320 118 L0 118 Z"
                fill="url(#{gid})"
              />
              <path
                d="M0 96 L42 90 L84 74 L126 80 L168 62 L210 54 L252 44 L294 36 L320 26"
                fill="none"
                stroke="var(--primary)"
                stroke-width="2.25"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <circle cx="320" cy="26" r="4" fill="var(--surface)" stroke="var(--primary)" stroke-width="2" />
            </svg>
            <figcaption>
              Stylized dashboard curve for narrative context — not live client metrics. Reporting ties to your analytics and CRM definitions.
            </figcaption>
          </figure>
"""


def figure_compact(gid: str) -> str:
    """Smaller caption for TOC sidebar."""
    return f"""          <figure class="signal-board">
            <div class="signal-board__top">
              <span class="signal-board__title">Organic sessions</span>
              <span class="signal-board__pill">Illustrative</span>
            </div>
            <svg viewBox="0 0 320 118" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <defs>
                <linearGradient id="{gid}" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stop-color="var(--primary)" stop-opacity="0.38" />
                  <stop offset="100%" stop-color="var(--primary)" stop-opacity="0" />
                </linearGradient>
              </defs>
              <g opacity="0.55" stroke="var(--border)" stroke-width="0.75">
                <line x1="0" y1="28" x2="320" y2="28" />
                <line x1="0" y1="56" x2="320" y2="56" />
                <line x1="0" y1="84" x2="320" y2="84" />
              </g>
              <path
                d="M0 96 L42 90 L84 74 L126 80 L168 62 L210 54 L252 44 L294 36 L320 26 L320 118 L0 118 Z"
                fill="url(#{gid})"
              />
              <path
                d="M0 96 L42 90 L84 74 L126 80 L168 62 L210 54 L252 44 L294 36 L320 26"
                fill="none"
                stroke="var(--primary)"
                stroke-width="2.25"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <circle cx="320" cy="26" r="4" fill="var(--surface)" stroke="var(--primary)" stroke-width="2" />
            </svg>
            <figcaption>Illustrative trend — not live metrics.</figcaption>
          </figure>
"""


ICONS = {
    "search": """              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>""",
    "trend": """              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>""",
    "exec": """              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 17v-6h6v6m-7 4h8a2 2 0 002-2V7l-4-4H7a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>""",
}


def visual_strip(
    *,
    aria: str,
    kicker: str,
    h2: str,
    t1: str,
    p1: str,
    t2: str,
    p2: str,
    t3: str,
    p3: str,
) -> str:
    return f"""    <section class="section section-sm section-band" aria-label="{aria}">
      <div class="container">
        <div class="section-band-head">
          <span class="kicker">{kicker}</span>
          <h2 style="font-size: 1.35rem; margin: 0.35rem 0 0;">{h2}</h2>
        </div>
        <div class="visual-strip">
          <article class="visual-pillar">
            <div class="visual-pillar__icon" aria-hidden="true">
{ICONS["search"]}
            </div>
            <h3>{t1}</h3>
            <p>{p1}</p>
          </article>
          <article class="visual-pillar">
            <div class="visual-pillar__icon" aria-hidden="true">
{ICONS["trend"]}
            </div>
            <h3>{t2}</h3>
            <p>{p2}</p>
          </article>
          <article class="visual-pillar">
            <div class="visual-pillar__icon" aria-hidden="true">
{ICONS["exec"]}
            </div>
            <h3>{t3}</h3>
            <p>{p3}</p>
          </article>
        </div>
      </div>
    </section>
"""


def prepend_after_main_open(html: str, insert: str) -> str:
    """Insert right after <main id=\"main\">"""
    return html.replace('<main id="main">', '<main id="main">\n' + insert, 1)


def patch_text(path: Path, new: str) -> None:
    old = path.read_text(encoding="utf-8")
    if old == new:
        return
    path.write_text(new, encoding="utf-8")
    print(f"updated {path.relative_to(ROOT)}")


def main() -> None:
    # --- About: upgrade aside ---
    about = ROOT / "about" / "index.html"
    a = about.read_text(encoding="utf-8")
    if 'hero-panel--signal' not in a:
        a = a.replace(
            '<aside class="hero-panel">',
            '<aside class="hero-panel hero-panel--signal">\n' + figure_block("sigAbout"),
            1,
        )
    band_about = visual_strip(
        aria="Operator lens",
        kicker="Commercial SEO discipline",
        h2="Depth where it matters — clarity where executives sit.",
        t1="Systems thinking",
        p1="Technical and entity signals aligned to revenue pages and funnel truth.",
        t2="Pipeline vocabulary",
        p2="Goals and conversions framed so marketing and leadership share one narrative.",
        t3="Direct accountability",
        p3="Operator-led delivery without an opaque fulfillment layer.",
    )
    if "section-band" not in a.split("</section>", 2)[0]:
        a = a.replace(
            "    </section>\n\n    <section class=\"section section-sm\">",
            "    </section>\n\n" + band_about + "\n    <section class=\"section section-sm\">",
            1,
        )
    patch_text(about, a)

    # --- Services hub: replace hero ---
    svc_idx = ROOT / "services" / "index.html"
    s = svc_idx.read_text(encoding="utf-8")
    old_hero = """    <section class="section hero">
      <div class="container">
        <span class="kicker">Service catalog</span>
        <h1>SEO services tailored to business model, geography, and growth stage.</h1>
        <p>Use starter audits for fast diagnosis, then move into custom retainers for implementation. This model avoids one-size-fits-all pricing and keeps execution aligned to your targets.</p>
      </div>
    </section>"""
    new_hero = """    <section class="section hero">
      <div class="container hero-grid">
        <div class="hero-copy">
          <span class="kicker">Service catalog</span>
          <h1>SEO services tailored to business model, geography, and growth stage.</h1>
          <p>Use starter audits for fast diagnosis, then move into custom retainers for implementation. This model avoids one-size-fits-all pricing and keeps execution aligned to your targets.</p>
        </div>
        <aside class="hero-panel hero-panel--signal" aria-label="Catalog snapshot">
""" + figure_block(
        "sigSvcIdx"
    )
    new_hero += """          <span class="kicker">Catalog snapshot</span>
          <div class="metric-grid">
            <div class="metric">
              <span class="label">Service lines</span>
              <span class="value">4</span>
            </div>
            <div class="metric">
              <span class="label">Pricing shape</span>
              <span class="value">Audit + scale</span>
            </div>
            <div class="metric">
              <span class="label">Markets</span>
              <span class="value">US · CA · AU · EU</span>
            </div>
          </div>
          <p>Choose a line item below for scope detail and starter diagnostic options.</p>
          <div class="hero-actions">
            <a class="btn btn-secondary" href="./technical-seo.html">Technical SEO</a>
            <a class="btn btn-secondary" href="./local-seo.html">Local SEO</a>
          </div>
        </aside>
      </div>
    </section>"""
    if old_hero in s:
        s = s.replace(old_hero, new_hero, 1)
    band_svc = visual_strip(
        aria="Service economics",
        kicker="Catalog lens",
        h2="Every engagement routes through diagnostics, prioritization, and proof — not vanity dashboards.",
        t1="Discovery depth",
        p1="Technical, intent, and conversion friction mapped before roadmap commitments.",
        t2="Hybrid pricing",
        p2="Starter audits for speed; retainers sized to market complexity and velocity.",
        t3="Evidence-led wins",
        p3="Reporting anchored to analytics definitions your stakeholders already trust.",
    )
    if "section-band" not in s:
        s = s.replace(
            "    </section>\n\n    <section class=\"section\">",
            "    </section>\n\n" + band_svc + "\n    <section class=\"section\">",
            1,
        )
    patch_text(svc_idx, s)

    # --- Service detail pages ---
    service_bands = {
        "technical-seo.html": (
            "sigTech",
            "Technical SEO lens",
            "Ship crawl clarity and speed discipline before chasing new content volume.",
            "Crawl integrity",
            "Resolve conflicts that waste budget on non-revenue URLs.",
            "Performance truth",
            "Core Web Vitals and path-level speed tied to money pages.",
            "Index governance",
            "Canonicals, schema, and internal links that defend rankings.",
        ),
        "local-seo.html": (
            "sigLocal",
            "Local SEO lens",
            "Maps, landing pages, and reputation signals working as one system.",
            "Map relevance",
            "Profiles and categories aligned to service intent and geography.",
            "Location pages",
            "Proof-rich landing depth without doorway patterns.",
            "Trust loops",
            "Reviews and citations feeding local authority responsibly.",
        ),
        "international-seo.html": (
            "sigIntl",
            "International SEO lens",
            "Market expansion without breaking technical governance.",
            "Market targeting",
            "Intent and SERP reality per region before URL decisions.",
            "Hreflang discipline",
            "Locale clusters that prevent cannibalization and dilution.",
            "Operational scale",
            "Governance that survives CMS edits and franchise drift.",
        ),
        "content-seo.html": (
            "sigContent",
            "Content SEO lens",
            "Editorial systems that compound authority instead of chasing volume.",
            "Intent architecture",
            "Clusters mapped to buyer progression and revenue pages.",
            "Internal linking",
            "Hub-spoke signals that reinforce entities and crawl paths.",
            "Refresh cadence",
            "Update logic tied to performance data — not arbitrary calendars.",
        ),
    }

    for fname, spec in service_bands.items():
        gid = spec[0]
        path = ROOT / "services" / fname
        raw = path.read_text(encoding="utf-8")
        if "hero-panel--signal" not in raw:
            raw = raw.replace(
                '<aside class="hero-panel">',
                '<aside class="hero-panel hero-panel--signal">\n' + figure_block(gid),
                1,
            )
        band = visual_strip(
            aria=spec[1],
            kicker=spec[1].split(" lens")[0] if " lens" in spec[1] else spec[1],
            h2=spec[2],
            t1=spec[3],
            p1=spec[4],
            t2=spec[5],
            p2=spec[6],
            t3=spec[7],
            p3=spec[8],
        )
        if "section-band" not in raw.split("<main", 1)[1].split("</section>", 3)[0]:
            raw = re.sub(
                r"(    </section>\s*\n)(\s*<section class=\"section\">)",
                r"\1\n" + band + r"\n\2",
                raw,
                count=1,
            )
        patch_text(path, raw)

    # --- Contact ---
    cpath = ROOT / "contact" / "index.html"
    c = cpath.read_text(encoding="utf-8")
    if "hero-panel--signal" not in c:
        c = c.replace(
            '<aside class="hero-panel">',
            '<aside class="hero-panel hero-panel--signal">\n' + figure_block("sigContact"),
            1,
        )
    band_c = visual_strip(
        aria="Engagement lens",
        kicker="Next steps",
        h2="Share goals and constraints — receive a realistic scope and timeline.",
        t1="Fast triage",
        p1="Business model, market, and technical baseline reviewed before proposals.",
        t2="Clear handoff",
        p2="Direct recommendations without agency theater or hidden layers.",
        t3="Proof-first posture",
        p3="Expect questions that align SEO work to pipeline definitions you already track.",
    )
    if "section-band" not in c:
        c = c.replace(
            "    </section>\n\n    <section class=\"section\">",
            "    </section>\n\n" + band_c + "\n    <section class=\"section\">",
            1,
        )
    patch_text(cpath, c)

    # --- Case studies index ---
    cs = ROOT / "case-studies" / "index.html"
    cs_raw = cs.read_text(encoding="utf-8")
    old_cs_hero = """    <section class="section hero">
      <div class="container">
        <span class="kicker">Case study hub</span>
        <h1>Public case studies and implementation references.</h1>
        <p>Each case includes scope, execution details, artifact links, and a transparency note so skeptical buyers can validate the work quality.</p>
      </div>
    </section>"""
    new_cs_hero = """    <section class="section hero">
      <div class="container hero-grid">
        <div class="hero-copy">
          <span class="kicker">Case study hub</span>
          <h1>Public case studies and implementation references.</h1>
          <p>Each case includes scope, execution details, artifact links, and a transparency note so skeptical buyers can validate the work quality.</p>
        </div>
        <aside class="hero-panel hero-panel--signal" aria-label="Evidence snapshot">
""" + figure_block(
        "sigCases"
    )
    new_cs_hero += """          <span class="kicker">Evidence snapshot</span>
          <div class="metric-grid">
            <div class="metric">
              <span class="label">Transparency</span>
              <span class="value">Artifacts</span>
            </div>
            <div class="metric">
              <span class="label">Depth</span>
              <span class="value">Technical + growth</span>
            </div>
            <div class="metric">
              <span class="label">Validation</span>
              <span class="value">Live links</span>
            </div>
          </div>
          <p>Drill into implementation notes and external references for each story.</p>
          <div class="hero-actions">
            <a class="btn btn-secondary" href="../mentions.html">Mentions and proof</a>
          </div>
        </aside>
      </div>
    </section>"""
    if old_cs_hero in cs_raw:
        cs_raw = cs_raw.replace(old_cs_hero, new_cs_hero, 1)
    band_cs = visual_strip(
        aria="Case lens",
        kicker="Proof economics",
        h2="Show the work: scope, execution path, and outcomes buyers can inspect.",
        t1="Context clarity",
        p1="Business constraints and technical reality stated before tactics.",
        t2="Execution trail",
        p2="Repositories, screenshots, and references that hold up to scrutiny.",
        t3="Outcome honesty",
        p3="No fabricated testimonials — narrative aligned to verifiable signals.",
    )
    if "section-band" not in cs_raw:
        cs_raw = cs_raw.replace(
            "    </section>\n\n    <section class=\"section\">",
            "    </section>\n\n" + band_cs + "\n    <section class=\"section\">",
            1,
        )
    patch_text(cs, cs_raw)

    # --- Blog index ---
    blog = ROOT / "blog" / "index.html"
    b = blog.read_text(encoding="utf-8")
    old_blog = """    <section class="section hero">
      <div class="container">
        <span class="kicker">SEO blog</span>
        <h1>Practical SEO insights built for execution, not theory.</h1>
        <p>Posts are drafted twice weekly through a trend-and-keyword workflow and reviewed before publishing. Every article follows quality checks for readability, EEAT, and business relevance.</p>
      </div>
    </section>"""
    new_blog = """    <section class="section hero">
      <div class="container hero-grid">
        <div class="hero-copy">
          <span class="kicker">SEO blog</span>
          <h1>Practical SEO insights built for execution, not theory.</h1>
          <p>Posts are drafted twice weekly through a trend-and-keyword workflow and reviewed before publishing. Every article follows quality checks for readability, EEAT, and business relevance.</p>
        </div>
        <aside class="hero-panel hero-panel--signal" aria-label="Editorial snapshot">
""" + figure_block(
        "sigBlog"
    )
    new_blog += """          <span class="kicker">Editorial snapshot</span>
          <div class="metric-grid">
            <div class="metric">
              <span class="label">Cadence</span>
              <span class="value">2× weekly drafts</span>
            </div>
            <div class="metric">
              <span class="label">Quality gate</span>
              <span class="value">Manual review</span>
            </div>
            <div class="metric">
              <span class="label">Focus</span>
              <span class="value">EEAT + action</span>
            </div>
          </div>
          <p>Use clusters below as topical anchors for authority building.</p>
          <div class="hero-actions">
            <a class="btn btn-secondary" href="../services/content-seo.html">Content SEO service</a>
          </div>
        </aside>
      </div>
    </section>"""
    if old_blog in b:
        b = b.replace(old_blog, new_blog, 1)
    band_b = visual_strip(
        aria="Editorial lens",
        kicker="Authority economics",
        h2="Publish with intent maps — not disconnected keyword articles.",
        t1="Signal-informed drafts",
        p1="Trend and keyword inputs routed through human editorial judgment.",
        t2="Structured depth",
        p2="Headings and entities built for classic SERPs and answer surfaces.",
        t3="Internal pathways",
        p3="Clusters that reinforce services, proof, and conversion pages.",
    )
    if "section-band" not in b:
        b = b.replace(
            "    </section>\n\n    <section class=\"section\">",
            "    </section>\n\n" + band_b + "\n    <section class=\"section\">",
            1,
        )
    patch_text(blog, b)

    # --- Mentions (root-relative paths) ---
    mpath = ROOT / "mentions.html"
    m = mpath.read_text(encoding="utf-8")
    old_m = """    <section class="section hero">
      <div class="container">
        <span class="kicker">Public references</span>
        <h1>Mentions, repositories, and proof signals.</h1>
        <p>This page lists public references that validate project experience and execution quality.</p>
      </div>
    </section>"""
    new_m = """    <section class="section hero">
      <div class="container hero-grid">
        <div class="hero-copy">
          <span class="kicker">Public references</span>
          <h1>Mentions, repositories, and proof signals.</h1>
          <p>This page lists public references that validate project experience and execution quality.</p>
        </div>
        <aside class="hero-panel hero-panel--signal" aria-label="Trust snapshot">
""" + figure_block(
        "sigMentions"
    )
    new_m += """          <span class="kicker">Trust snapshot</span>
          <div class="metric-grid">
            <div class="metric">
              <span class="label">Identity</span>
              <span class="value">Verifiable</span>
            </div>
            <div class="metric">
              <span class="label">Artifacts</span>
              <span class="value">Public</span>
            </div>
            <div class="metric">
              <span class="label">Performance</span>
              <span class="value">Benchmarked</span>
            </div>
          </div>
          <p>Cross-check profiles, repos, and Lighthouse references before engaging.</p>
          <div class="hero-actions">
            <a class="btn btn-secondary" href="./about/index.html">About</a>
          </div>
        </aside>
      </div>
    </section>"""
    if old_m in m:
        m = m.replace(old_m, new_m, 1)
    band_m = visual_strip(
        aria="Proof lens",
        kicker="Verification economics",
        h2="Earned credibility beats anonymous claims — especially in SEO.",
        t1="Public footprint",
        p1="Profiles and repositories buyers can inspect without NDAs.",
        t2="Technical receipts",
        p2="Performance and implementation signals tied to named work.",
        t3="Ethical posture",
        p3="No fabricated testimonials or ranking guarantees.",
    )
    if "section-band" not in m:
        m = m.replace(
            "    </section>\n\n    <section class=\"section\">",
            "    </section>\n\n" + band_m + "\n    <section class=\"section\">",
            1,
        )
    patch_text(mpath, m)

    # --- Free tool ---
    ft = ROOT / "free-tools" / "gsc-error-priority-calculator.html"
    ftr = ft.read_text(encoding="utf-8")
    if "hero-panel--signal" not in ftr:
        ftr = ftr.replace(
            '<aside class="hero-panel">',
            '<aside class="hero-panel hero-panel--signal">\n' + figure_block("sigTool"),
            1,
        )
    band_ft = visual_strip(
        aria="Prioritization lens",
        kicker="Sprint economics",
        h2="Rank fixes by revenue touchpoints — not spreadsheet anxiety.",
        t1="Impact weighting",
        p1="Business and URL value inform what earns developer time first.",
        t2="Effort realism",
        p2="Subtracts fantasy priorities that stall engineering.",
        t3="Stakeholder narrative",
        p3="Scores export cleanly into roadmap conversations.",
    )
    if "section-band" not in ftr:
        ftr = ftr.replace(
            "    </section>\n\n    <section class=\"section\">",
            "    </section>\n\n" + band_ft + "\n    <section class=\"section\">",
            1,
        )
    patch_text(ft, ftr)

    print("done")


if __name__ == "__main__":
    main()
