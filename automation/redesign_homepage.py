#!/usr/bin/env python3
"""Apply flagship homepage structure."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

MAIN = """
  <main id="main">
    <section class="section hero hero--flagship">
      <div class="container hero-grid">
        <motion class="hero-copy">
          <span class="kicker">Pipeline-first SEO studio</span>
          <h1>Organic growth engineered for revenue, not ranking vanity.</h1>
          <p class="lede">SEO With Faiz is the commercial SEO practice of Mohd Faizuddin Ahmed — built for B2B and service companies in the USA, Canada, Australia, and Europe that need qualified pipeline across classic search and AI answer surfaces.</p>
          <div class="answer-box" aria-label="Quick answer">
            <p><strong>Quick answer:</strong> Start with a technical and intent diagnostic, then execute monthly priorities tied to pipeline metrics — not vanity rank reports.</p>
          </div>
          <div class="badge-row">
            <span class="badge">Technical SEO</span>
            <span class="badge">Local SEO</span>
            <span class="badge">International SEO</span>
            <span class="badge">AEO + GEO</span>
          </div>
          <div class="hero-actions">
            <a class="btn btn-primary" data-dynamic-cta href="./contact/index.html">Book strategy call</a>
            <a class="btn btn-secondary" href="./services/index.html">Explore services</a>
            <a class="btn btn-secondary" href="./case-studies/index.html">Review proof library</a>
          </div>
        </div>
        <aside class="studio-panel" aria-label="Engagement snapshot">
          <span class="kicker">Operating snapshot</span>
          <ul class="studio-panel__list">
            <li><span>Delivery model</span><strong>Audit → retainer</strong></li>
            <li><span>Performance baseline</span><strong>Lighthouse 95+</strong></li>
            <li><span>Markets served</span><strong>US · CA · AU · EU</strong></li>
            <li><span>Response window</span><strong>24 business hours</strong></li>
          </ul>
          <p>Public artifacts, case studies, and implementation notes are available before you book a call.</p>
          <div class="hero-actions">
            <a class="btn btn-secondary" href="./mentions.html">Mentions and proof</a>
            <a class="btn btn-secondary" href="./resources/seo-audit-playbook.html">SEO playbook</a>
          </div>
        </aside>
      </div>
    </section>

    <section class="section section-sm" aria-label="Studio metrics">
      <div class="container stat-ribbon">
        <article class="stat-ribbon__item">
          <span class="stat-ribbon__label">Proof assets</span>
          <span class="stat-ribbon__value">4 public builds</span>
        </article>
        <article class="stat-ribbon__item">
          <span class="stat-ribbon__label">Starter audit</span>
          <span class="stat-ribbon__value">USD 100</span>
        </article>
        <article class="stat-ribbon__item">
          <span class="stat-ribbon__label">Schema graph</span>
          <span class="stat-ribbon__value">Entity-led</span>
        </article>
        <article class="stat-ribbon__item">
          <span class="stat-ribbon__label">Reporting</span>
          <span class="stat-ribbon__value">Pipeline-first</span>
        </article>
      </div>
    </section>

    <section class="section" aria-label="Proof library">
      <div class="container">
        <span class="kicker">Proof library</span>
        <h2>Public work you can inspect before you hire.</h2>
        <p class="lede">No fabricated logos. These are the builds, audits, and tools already published on seowithfaiz.com.</p>
        <div class="proof-grid" style="margin-top:1.25rem;">
          <a class="proof-card" href="./case-studies/unstop-seo-audit.html">
            <div class="proof-card__media"><img src="./assets/projects/unstop-seo-audit.png" alt="Unstop SEO audit framework screenshot" width="640" height="360" loading="lazy" decoding="async"></div>
            <span class="proof-card__eyebrow">Audit framework</span>
            <h3>Unstop SEO diagnostic model</h3>
            <p>Structured technical, content, and prioritization workflow with public references.</p>
          </a>
          <a class="proof-card" href="./case-studies/hyderabad-globe-fc.html">
            <div class="proof-card__media"><img src="./assets/projects/telangana-stride-hub.jpg" alt="Hyderabad Globe FC project screenshot" width="640" height="360" loading="lazy" decoding="async"></div>
            <span class="proof-card__eyebrow">Technical rebuild</span>
            <h3>Hyderabad Globe FC</h3>
            <p>Performance-led rebuild with local discoverability and implementation notes.</p>
          </a>
          <a class="proof-card" href="./free-tools/gsc-error-priority-calculator.html">
            <motion class="proof-card__media"><img src="./assets/projects/lighthouse-global-scores-proof.png" alt="Lighthouse performance proof screenshot" width="640" height="360" loading="lazy" decoding="async"></div>
            <span class="proof-card__eyebrow">Free tool</span>
            <h3>GSC error priority calculator</h3>
            <p>Impact-weighted technical queue scoring for dev and SEO alignment.</p>
          </a>
          <a class="proof-card" href="./resources/seo-audit-playbook.html">
            <motion class="proof-card__media"><img src="./assets/projects/100hires.png" alt="SEO audit playbook resource preview" width="640" height="360" loading="lazy" decoding="async"></div>
            <span class="proof-card__eyebrow">Resource</span>
            <h3>SEO audit playbook</h3>
            <p>Operator checklist for technical integrity, intent coverage, and execution sequencing.</p>
          </a>
        </div>
      </div>
    </section>

    <section class="section section-sm section-band" aria-label="Core outcomes">
      <div class="container">
        <div class="section-band-head">
          <span class="kicker">Search economics</span>
          <h2>Visibility, intent, and proof — without vanity charts.</h2>
        </div>
        <div class="visual-strip">
          <article class="visual-pillar">
            <div class="visual-pillar__icon" aria-hidden="true">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
            </div>
            <h3>Qualified discovery</h3>
            <p>Entity-rich pages and structured data tuned for classic SERPs and AI summaries.</p>
          </article>
          <article class="visual-pillar">
            <div class="visual-pillar__icon" aria-hidden="true">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
            </div>
            <h3>Pipeline signals</h3>
            <p>Goals, events, and CRM-ready narratives — not ranking screenshots alone.</p>
          </article>
          <article class="visual-pillar">
            <div class="visual-pillar__icon" aria-hidden="true">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 17v-6h6v6m-7 4h8a2 2 0 002-2V7l-4-4H7a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
            </div>
            <h3>Executive clarity</h3>
            <p>Prioritized roadmaps and sprint cadence your stakeholders can defend internally.</p>
          </article>
        </div>
      </div>
    </section>

    <section class="section section-sm">
      <div class="container editorial-split">
        <article class="card">
          <span class="kicker">Human trust layer</span>
          <img class="profile-headshot" src="./assets/profile/faiz-headshot.png" alt="Mohd Faizuddin Ahmed headshot" width="360" height="360" loading="lazy" decoding="async">
          <h2>You work directly with Faiz, not a hidden delivery chain.</h2>
          <p>I personally lead discovery, technical diagnostics, priority mapping, and execution guidance.</p>
          <ul>
            <li>Single owner for strategy and implementation direction</li>
            <li>No outsourced handoff between sales and execution</li>
            <li>Transparent constraints, assumptions, and trade-off calls</li>
          </ul>
          <a href="./about/index.html">Review full profile and operating model</a>
        </article>
        <article class="card">
          <span class="kicker">External validation</span>
          <h2>Identity and proof are publicly verifiable.</h2>
          <ul>
            <li><a href="https://www.linkedin.com/in/mohd-faizuddin-ahmed-4984a0148" target="_blank" rel="noopener noreferrer">LinkedIn profile and professional history</a></li>
            <li><a href="https://github.com/FNGK" target="_blank" rel="noopener noreferrer">GitHub repositories tied to SEO projects</a></li>
            <li><a href="./case-studies/index.html">Case studies with live links and repository references</a></li>
          </ul>
          <div class="cert-logo-row" aria-label="Certification logos">
            <a class="cert-logo" href="https://skillshop.credential.net/profile/mohdfaizuddinahmed380115/wallet" target="_blank" rel="noopener noreferrer" aria-label="Google Ads certification logo in credential wallet"><img src="./assets/logos/google-ads.svg" alt="Google Ads logo" width="48" height="48" loading="lazy" decoding="async"></a>
            <a class="cert-logo" href="https://skillshop.credential.net/profile/mohdfaizuddinahmed380115/wallet" target="_blank" rel="noopener noreferrer" aria-label="Google Analytics certification logo in credential wallet"><img src="./assets/logos/google-analytics.svg" alt="Google Analytics logo" width="48" height="48" loading="lazy" decoding="async"></a>
            <a class="cert-logo" href="https://skillshop.credential.net/profile/mohdfaizuddinahmed380115/wallet" target="_blank" rel="noopener noreferrer" aria-label="upGrad certification logo in credential wallet"><img src="./assets/logos/upgrad.svg" alt="upGrad logo" width="124" height="32" loading="lazy" decoding="async"></a>
          </div>
          <p>No fabricated testimonials, no ranking guarantees, and no anonymous ghost team claims.</p>
        </article>
      </div>
    </section>

    <section class="section section-sm">
      <div class="container">
        <span class="kicker">Services</span>
        <h2>Global SEO services with hybrid pricing.</h2>
        <p class="lede">Start with a focused diagnostic engagement, then scale into implementation retainers built around your market and growth stage.</p>
        <div class="grid-2" style="margin-top:1rem;">
          <article class="card">
            <h3>Starter SEO audit</h3>
            <p>Best for teams that need clear technical and on-page priorities before investing in full implementation.</p>
            <ul>
              <li>Technical SEO and architecture review (up to 10 core pages)</li>
              <li>Intent and content gap map</li>
              <li>30-day action roadmap with priority stack</li>
            </ul>
            <p><strong>Starter pricing:</strong> USD 100 (upfront)</p>
            <a class="btn btn-secondary" href="./services/technical-seo.html">View scope</a>
          </article>
          <article class="card">
            <h3>Custom growth retainers</h3>
            <p>For companies ready to execute monthly SEO implementation and reporting across target markets.</p>
            <ul>
              <li>Technical fixes and content operations</li>
              <li>Local and international market expansion</li>
              <li>Monthly performance and pipeline reporting</li>
            </ul>
            <p><strong>Pricing model:</strong> custom scope by market, site size, and growth targets.</p>
            <a class="btn btn-secondary" href="./services/index.html">Compare services</a>
          </article>
        </div>
      </div>
    </section>

    <section class="section section--ink">
      <div class="container">
        <span class="kicker">AEO and GEO on this site</span>
        <h2>Answer-engine readiness is implemented, not promised.</h2>
        <div class="grid-3" style="margin-top:1rem;">
          <article class="card">
            <h3>Structured data graph</h3>
            <p>WebSite, Organization, ProfessionalService, FAQPage, HowTo, ItemList, and SpeakableSpecification across key URLs.</p>
          </article>
          <article class="card">
            <h3>Answer-first architecture</h3>
            <p>Quick-answer blocks, semantic headings, and intent-to-CTA paths on commercial and resource pages.</p>
          </article>
          <article class="card">
            <h3>Entity and authority mapping</h3>
            <p>Internal clusters, case evidence, external profile links, and proof pages reinforce topical depth.</p>
          </article>
        </div>
      </div>
    </section>

    <section class="section section-sm">
      <div class="container">
        <span class="kicker">Markets</span>
        <h2>Built for cross-border commercial SEO.</h2>
        <div class="market-strip" style="margin-top:1rem;">
          <span class="market-strip__item">United States</span>
          <span class="market-strip__item">Canada</span>
          <span class="market-strip__item">Australia</span>
          <span class="market-strip__item">Europe</span>
          <span class="market-strip__item">India</span>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <span class="kicker">Frequently asked questions</span>
        <h2>Direct answers before you schedule a strategy call.</h2>
        <div class="faq-list" id="faq">
          <article class="faq-item">
            <h3>Do you work with all business categories?</h3>
            <p>I work with legitimate businesses across most industries. I do not accept projects in adult services, alcohol, or interest-led lending categories.</p>
          </article>
          <article class="faq-item">
            <h3>Do you guarantee ranking positions?</h3>
            <p>No ethical SEO partner can guarantee fixed rankings. I commit to transparent execution, technical quality, and measurable business-focused progress.</p>
          </article>
          <article class="faq-item">
            <h3>Can you support in-house teams?</h3>
            <p>Yes. I can operate as an external SEO lead, collaborate with in-house content and dev teams, and provide implementation guidance.</p>
          </article>
          <article class="faq-item">
            <h3>How quickly can we start?</h3>
            <p>Starter audits typically begin within a few business days after scope confirmation and payment.</p>
          </article>
        </div>
      </div>
    </section>

    <section class="section cta-band">
      <div class="container grid-2">
        <div class="page-intro">
          <span class="kicker cta-kicker">Primary call to action</span>
          <h2 class="cta-heading">Need SEO that survives algorithm changes and AI search shifts?</h2>
          <p>I will review your site, identify the highest-impact opportunities, and provide a practical action plan aligned to your growth target.</p>
          <div class="hero-actions">
            <a class="btn btn-primary" data-dynamic-cta href="./contact/index.html">Book strategy call</a>
            <a class="btn btn-secondary" href="mailto:md.faiz.ahmed62@gmail.com">Email direct</a>
          </div>
        </div>
        <article class="card cta-card">
          <h3>Quick contact</h3>
          <p><strong>Email:</strong> <a href="mailto:md.faiz.ahmed62@gmail.com">md.faiz.ahmed62@gmail.com</a></p>
          <p><strong>WhatsApp:</strong> <a href="https://wa.me/916281367104" target="_blank" rel="noopener noreferrer">+91 62813 67104</a></p>
          <p><strong>Primary regions:</strong> USA, Canada, Australia, Europe</p>
          <p><strong>Response time:</strong> within 24 business hours</p>
        </article>
      </div>
    </section>
  </main>
""".replace("<motion", "<div").replace("</motion>", "</div>")


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    updated = re.sub(r"<main id=\"main\">[\s\S]*?</main>", MAIN.strip(), html, count=1)
    INDEX.write_text(updated, encoding="utf-8")
    print("Homepage main content replaced.")


if __name__ == "__main__":
    main()
