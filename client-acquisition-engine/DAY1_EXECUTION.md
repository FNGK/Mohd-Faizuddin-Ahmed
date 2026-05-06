# Day 1 Execution (Immediate Start)

## 0:00 - 0:45 (Setup)

- Import CRM and Daily CSV templates into Google Sheets.
- Add Apps Script and run `runDailyEngine` once.
- Keep `AUTO_SEND = false` for quality control.

## 0:45 - 2:00 (Lead Build)

- Collect first 30 leads from one niche only.
- Fill at least: business, website, contact, email, offer fit.
- Set `Sequence_Step = 1`, `Status = New`.

## 2:00 - 3:30 (GPT Value Pass)

- Use `prompts/micro_audit_prompt.md` for each lead.
- Fill `Issue_1`, `Issue_2`, `Issue_3`, `Quick_Win`, `Target_Page`.
- Skip leads with fit score under 3.

## 3:30 - 4:30 (Message Drafting)

- Use `prompts/personalized_outreach_prompt.md`.
- Generate one high-quality message per lead.
- Push final message into Gmail drafts.

## 4:30 - 5:00 (Send + Follow-Up)

- Send first 15 personalized messages.
- Set `Last_Touch_Date = today`.
- Set `Next_Follow_Up = today + 3 days`.
- Keep status updated in CRM.

## End of Day Target

- 30 leads created.
- 15 quality messages sent.
- 15 next follow-ups scheduled.
- Pipeline engine active for tomorrow.
