# Automation Runbook (Google Sheets + Apps Script)

## What This Automation Does

- Initializes missing CRM defaults (`Sequence_Step`, `Status`).
- Marks due follow-ups based on `Next_Follow_Up`.
- Creates Gmail drafts (or sends emails if enabled).
- Updates touch dates and next follow-up dates.
- Writes a daily touch summary into `Daily` sheet.

## Safety Mode

- `AUTO_SEND` is `false` by default.
- Default behavior: creates drafts for review before sending.
- Set `AUTO_SEND = true` only after validating your message quality.

## Required Sheet Tabs

- `Leads` (from `templates/leads_crm_template.csv`)
- `Daily` (from `templates/daily_dashboard_template.csv`)

## Required Headers In `Leads`

- `Email`
- `Sequence_Step`
- `Status`
- `Last_Touch_Date`
- `Next_Follow_Up`
- `Outreach_Channel`

## Install Steps

1. Open your Google Sheet.
2. Go to Extensions -> Apps Script.
3. Paste `google_apps_script.gs` content.
4. Save and run `runDailyEngine` once.
5. Authorize script permissions.
6. Add a time trigger:
   - Function: `runDailyEngine`
   - Frequency: daily
   - Preferred time: morning.

## Menu Actions

After setup, use menu `Client Engine` in Sheets:

- `Run Daily Engine`
- `Initialize Missing Defaults`
- `Create Due Drafts Now`
- `Send Due Emails Now (Use Carefully)`

## Recommended Workflow

- Keep `AUTO_SEND` off for first 7 days.
- Review all drafts before sending.
- Measure reply quality and refine templates.
- Move to auto send only for proven templates and vetted lead lists.
