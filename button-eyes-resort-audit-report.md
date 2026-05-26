# Button Eyes Resort SEO Audit Report

Prepared for: Button Eyes Resort  
Prepared by: SEO With Faiz  
Date: 2026-05-25

## Executive Summary

Button Eyes Resort has a live website with indexable core pages, but the current SEO setup is weak enough to limit qualified organic growth. The biggest issues are not "the site is invisible"; they are that search engines are being given mixed-quality inputs: duplicate blog URLs, placeholder or irrelevant content on important pages, a broken sitemap reference, weak commercial intent targeting, and template leftovers that reduce trust and crawl clarity.

The source audit folder was useful, but not fully reliable on its own. Some items were incomplete because Google Search Console indexing data is still processing, and some findings were overstated or stale. To close those gaps, the audit below combines:

- the shared audit files,
- live verification of the public website on 2026-05-25,
- manual checks across core pages, blog URLs, robots, and sitemap behavior.

## Audit Scope Reviewed

Source materials reviewed:

- `Button Eyes - Indexing Issues`
- `Button Eyes - Page indexing - still processing`
- `Button Eyes Resort - URL Indexing`
- `Button Eyes resort Keyword list`
- `BUTTONEYES RESORT AUDIT SHEET`
- `GA4 And GSC Data`
- `Screaming Frog Crawl Data - Raw`

Live verification performed on:

- 11 core URLs
- 6 blog URLs plus 2 category URLs
- `robots.txt`
- sitemap endpoints referenced by the site

## What Matters Most

### 1. Crawl and discovery layer needs correction

The site's `robots.txt` points to `https://buttoneyes.in/sitemap_index.xml`, but that URL returns `404 Not Found`. This is a major technical issue because it weakens discovery and sends incorrect signals to search engines about where the site structure lives.

Why it matters:

- search engines lose a reliable discovery path,
- new or updated pages take longer to surface,
- index control becomes harder when duplicate or low-value URLs exist.

### 2. Duplicate blog URLs are indexable and self-canonicalized

The site has duplicate post pairs such as:

- `18-easy-steps-for-planning-your-next-trip/`
- `18-easy-steps-for-planning-your-next-trip-2/`
- `the-ultimate-guide-to-traveling-when-you-have-no-money/`
- `the-ultimate-guide-to-traveling-when-you-have-no-money-2/`
- `the-best-travel-insurance-companies-for-seniors/`
- `the-best-travel-insurance-companies-for-seniors-2/`

These duplicates are live, indexable, and each points to its own canonical URL instead of consolidating authority to one preferred version.

Why it matters:

- duplicates split relevance and crawl budget,
- thin content pages inflate the index with low-value URLs,
- future local resort pages have to compete with poor-quality legacy pages.

### 3. Important pages contain placeholder, generic, or irrelevant content

This is one of the biggest business problems in the audit.

Live checks found:

- the blog is populated with irrelevant travel-template posts,
- the FAQ page contains clear Lorem Ipsum placeholder content,
- the experiences page contains placeholder descriptions for multiple amenities,
- several commercial pages use generic copy that does not strongly target local resort intent.

Why it matters:

- Google gets weak topical signals,
- users do not get confidence-building answers,
- the site ranks poorly for high-intent local searches such as resort queries around Hyderabad, day outings, family stays, pet-friendly stays, and private pool stays.

### 4. A broken booking/search shortcode is visible on the frontend

The homepage, blog pages, and other pages visibly render the shortcode:

`[mphb_availability_search adults='1' children='0' check_in_date='' check_out_date='' attributes='' class='"]`

Why it matters:

- this damages trust immediately,
- it suggests incomplete template implementation,
- it creates a poor UX on pages that should support booking conversion.

### 5. Core page structure is inconsistent

Live checks confirmed:

- the homepage has no `H1`,
- the bookings page has no `H1`,
- the URL slug `/experinces/` is misspelled,
- some metadata is technically present but commercially weak or generic.

Examples:

- homepage meta description: `A Stitch In Time`
- amenities meta description: `Swimming Pool`
- contact page meta description contains the typo `Hyberabad`

Why it matters:

- commercial pages are not clearly aligned to target search intent,
- weak metadata reduces click-through potential,
- structural inconsistencies dilute relevance signals.

### 6. Mobile performance is still weak

The source audit reports the following performance indicators:

- mobile score: `34`
- desktop score: `65`
- FCP: `3.1s`
- LCP: `8.2s`
- CLS: `0.01`

The raw crawl also shows many heavy image assets and a large plugin/theme stack, which supports the performance concern even without relying only on the score screenshot.

Why it matters:

- slower pages hurt both rankings and conversion,
- mobile users are likely the dominant traffic segment for this kind of business,
- performance issues compound with weak content and poor UX.

## Findings Corrected After Live Verification

The original audit sheet is directionally useful, but these items needed correction or nuance:

### Open Graph and social metadata are present

The audit sheet marked OG/social metadata as missing. Live checks on sampled core pages found `og:title`, `og:description`, and `og:image` present.

What this means:

- the issue is not total absence,
- the issue is quality, consistency, and commercial usefulness.

### Structured data is present

The audit sheet marked structured data as missing. Live checks found JSON-LD schema present on sampled pages, including organization, website, webpage, and article-style markup.

What this means:

- the site has schema,
- but schema presence alone does not solve content quality, duplicate indexation, or local relevance problems.

### Alt text is not universally missing on sampled core pages

The audit sheet suggested broad image alt-text failure. Live checks on sampled core pages found image `alt` attributes present.

What this means:

- image SEO still needs work,
- but the bigger media issues appear to be asset weight, naming quality, and content prioritization rather than a blanket absence of alt text.

### Not every page is missing an H1

Several pages do have H1 headings. The issue is concentrated in the wrong places:

- homepage missing H1,
- bookings page missing H1,
- heading quality and hierarchy are inconsistent across key templates.

## Gaps That Still Remain

These are the parts of the audit that cannot be finalized with confidence yet:

### GSC indexing baseline is incomplete

The page indexing report is still processing. That means the exact coverage state, exclusions, and canonicalization issues inside Search Console are not yet fully visible.

### GA4 and GSC performance numbers are not yet dependable

The source notes say GA4 and Search Console were only configured on `21/05/2026`. That means:

- traffic baselines are still immature,
- query data is incomplete,
- conversion-quality insights are not yet ready for decision-making.

### No clean conversion benchmark is available yet

There is no dependable baseline yet for:

- organic leads,
- booking-assisted sessions,
- inquiry-to-booking conversion,
- top landing pages by revenue intent.

## Priority Action Plan

## Phase 1: Technical Stabilization

Timeline: Week 1 to Week 2

- Fix sitemap generation and ensure the live sitemap resolves correctly.
- Resubmit sitemap in Google Search Console.
- Remove, redirect, or canonicalize duplicate blog URLs.
- Remove visible shortcode output from public pages.
- Fix homepage and bookings page heading structure.
- Review indexability rules for low-value archives and category pages.

## Phase 2: On-Page and Content Cleanup

Timeline: Week 2 to Week 5

- Rewrite homepage copy around clear local resort intent.
- Rewrite FAQ content from placeholder text to real customer questions.
- Rewrite experiences page from placeholder blocks to actual amenity-led content.
- Replace or remove irrelevant travel-template blog posts.
- Rewrite metadata for all core commercial pages.
- Correct URL, spelling, and location quality issues.

## Phase 3: Local and Revenue SEO Layer

Timeline: Week 5 to Week 12

- Map pages to priority keywords from the keyword list.
- Build location-specific landing page architecture where justified.
- Improve internal linking between core stay, amenities, bookings, contact, and experience pages.
- Strengthen local entity signals, brand consistency, and trust elements.
- Set up reporting for impressions, clicks, calls, inquiry actions, and booking intent pages.

## Recommended KPIs for the Next 90 Days

The right short-term KPIs are operational, not vanity metrics:

- live valid sitemap submitted and crawled,
- duplicate blog URLs removed or consolidated,
- all core pages mapped to unique primary intent,
- all key commercial pages have unique title tags, meta descriptions, and H1s,
- placeholder copy removed from FAQ and experiences pages,
- homepage and bookings page conversion UX cleaned up,
- measurable improvement in Search Console indexed valid pages,
- measurable improvement in branded and non-branded impressions.

## Bottom-Line Assessment

Button Eyes Resort does not need a total rebuild to become search-eligible, but it does need disciplined cleanup before growth work will compound.

The core opportunity is strong:

- the business has a real local offering,
- the site already has indexable commercial pages,
- analytics and GSC setup has begun,
- there are clear keyword themes with local intent potential.

The current constraint is execution quality. Right now, the site looks like a hospitality business sitting on top of leftover template content, duplicate URLs, and incomplete SEO implementation. That is fixable, but only if technical cleanup and content cleanup happen before aggressive traffic generation.

## Evidence Snapshot

Examples confirmed during live review:

- `robots.txt` references a sitemap endpoint that returns 404.
- `/faq/` contains Lorem Ipsum placeholder questions and answers.
- `/experinces/` uses a misspelled URL and placeholder amenity descriptions.
- `/blog/` lists duplicate posts with repeated titles and generic excerpts.
- several pages visibly render a booking shortcode instead of a working booking/search interface.
- homepage and bookings page lack an H1.

## Recommended Client Positioning

This should be presented to the client as:

`Your site is live and indexable, but it is not yet search-ready for sustained growth. The fastest gains will come from fixing crawl discovery, removing duplicate low-value URLs, cleaning up placeholder content, and aligning commercial pages to real search intent.`
