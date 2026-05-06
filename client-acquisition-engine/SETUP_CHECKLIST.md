# Setup Checklist (One-Time)

## 1) Offer and Pricing

- [ ] Keep entry offers live on website:
  - SEO Audit: INR 3000 / USD 100
  - Local SEO Sprint: INR 3000 / USD 100
- [ ] Define backend retainer in your notes:
  - Implementation + reporting retainer (USD 800-1500 starter range).
- [ ] Create simple scope doc for each offer.

## 2) Lead CRM

- [ ] Import `templates/leads_crm_template.csv` into Google Sheets tab named `Leads`.
- [ ] Import `templates/daily_dashboard_template.csv` into tab named `Daily`.
- [ ] Freeze header row and enable filters.
- [ ] Add conditional color formatting for `Status`.

## 3) Automation

- [ ] Open Extensions -> Apps Script in the Google Sheet.
- [ ] Paste `automation/google_apps_script.gs`.
- [ ] Save and run `runDailyEngine` once for authorization.
- [ ] Create time trigger:
  - Function: `runDailyEngine`
  - Frequency: daily
  - Time: your local morning.

## 4) Outreach Assets

- [ ] Use `prompts/micro_audit_prompt.md` for lead-level insights.
- [ ] Use `prompts/personalized_outreach_prompt.md` for message drafts.
- [ ] Send messages using `outreach/three_step_sequence.md`.

## 5) Daily Execution

- [ ] Add 15 new leads.
- [ ] Generate 15 micro-audit notes.
- [ ] Send 15 personalized first-touch messages.
- [ ] Update follow-up date on every touched lead.

## 6) Weekly Review

- [ ] Review Daily dashboard totals.
- [ ] Kill weak messaging variants.
- [ ] Keep one niche and one offer focus until first close.
- [ ] Publish one new proof update (result snippet or workflow note).

## 7) Failure Triggers (Pivot Rules)

- [ ] If reply rate is below 5% after 100 touches -> rewrite opening line and niche.
- [ ] If calls booked are below 2 after 10 positive replies -> tighten CTA and remove friction.
- [ ] If close rate is below 20% after 10 calls -> improve diagnosis-to-offer transition script.
