const ENGINE_CONFIG = {
  LEADS_SHEET: 'Leads',
  DAILY_SHEET: 'Daily',
  AUTO_SEND: false, // Keep false until templates are validated.
  MAX_TOUCHES_PER_RUN: 25
};

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Client Engine')
    .addItem('Run Daily Engine', 'runDailyEngine')
    .addItem('Initialize Missing Defaults', 'initializeLeadsDefaults')
    .addSeparator()
    .addItem('Create Due Drafts Now', 'createDueDraftsNow')
    .addItem('Send Due Emails Now (Use Carefully)', 'sendDueEmailsNow')
    .addToUi();
}

function runDailyEngine() {
  const stats = blankStats_();
  initializeLeadsDefaults();
  markDueFollowups_();

  if (ENGINE_CONFIG.AUTO_SEND) {
    processDueTouches_(stats, true);
  } else {
    processDueTouches_(stats, false);
  }

  writeDailySnapshot_(stats);
}

function createDueDraftsNow() {
  const stats = blankStats_();
  processDueTouches_(stats, false);
  writeDailySnapshot_(stats);
}

function sendDueEmailsNow() {
  const stats = blankStats_();
  processDueTouches_(stats, true);
  writeDailySnapshot_(stats);
}

function initializeLeadsDefaults() {
  const { sheet, headerMap } = getLeadSheetAndHeaders_();
  const rows = getRows_(sheet, headerMap);
  const stepCol = headerMap.Sequence_Step;
  const statusCol = headerMap.Status;

  rows.forEach((row) => {
    const step = Number(row.Sequence_Step || 0);
    const status = String(row.Status || '').trim();
    if (!step) {
      sheet.getRange(row.__rowNum, stepCol).setValue(1);
    }
    if (!status) {
      sheet.getRange(row.__rowNum, statusCol).setValue('New');
    }
  });
}

function markDueFollowups_() {
  const { sheet, headerMap } = getLeadSheetAndHeaders_();
  const rows = getRows_(sheet, headerMap);
  const statusCol = headerMap.Status;
  const closedDealCol = headerMap.Closed_Deal;
  const nextFollowUpCol = headerMap.Next_Follow_Up;

  rows.forEach((row) => {
    const closedDeal = String(row.Closed_Deal || '').toLowerCase() === 'yes';
    const status = String(row.Status || '');
    const nextDate = parseDate_(row.Next_Follow_Up);
    const isDue = nextDate && isSameOrBeforeToday_(nextDate);
    const canAdvance = ['Sent', 'Draft Created', 'No Response', 'New'].includes(status);

    if (!closedDeal && isDue && canAdvance) {
      sheet.getRange(row.__rowNum, statusCol).setValue('Follow-up Due');
      if (closedDealCol) {
        sheet.getRange(row.__rowNum, closedDealCol).setValue(row.Closed_Deal || 'No');
      }
      if (nextFollowUpCol) {
        sheet.getRange(row.__rowNum, nextFollowUpCol).setValue(formatDate_(nextDate));
      }
    }
  });
}

function processDueTouches_(stats, sendMode) {
  const { sheet, headerMap } = getLeadSheetAndHeaders_();
  const rows = getRows_(sheet, headerMap);
  let processed = 0;

  rows.forEach((row) => {
    if (processed >= ENGINE_CONFIG.MAX_TOUCHES_PER_RUN) return;
    if (!isEligibleForTouch_(row)) return;

    const step = Number(row.Sequence_Step || 1);
    if (step < 1 || step > 3) return;

    const message = buildMessage_(row, step);
    if (!message) return;

    const email = String(row.Email || '').trim();
    if (sendMode) {
      GmailApp.sendEmail(email, message.subject, message.body);
      stats.emailsSent += 1;
    } else {
      GmailApp.createDraft(email, message.subject, message.body);
      stats.draftsCreated += 1;
    }

    if (step === 1) {
      stats.firstTouches += 1;
    } else {
      stats.followups += 1;
    }

    updateLeadAfterTouch_(sheet, headerMap, row.__rowNum, step, sendMode);
    processed += 1;
  });
}

function isEligibleForTouch_(row) {
  const status = String(row.Status || '');
  const channel = String(row.Outreach_Channel || 'Email');
  const fitScore = Number(row.Fit_Score_1_5 || 0);
  const closedDeal = String(row.Closed_Deal || '').toLowerCase() === 'yes';
  const today = formatDate_(new Date());

  if (closedDeal) return false;
  if (!String(row.Email || '').trim()) return false;
  if (channel.toLowerCase() !== 'email') return false;
  if (fitScore && fitScore < 3) return false;
  if (row.Last_Touch_Date && formatDate_(parseDate_(row.Last_Touch_Date)) === today) return false;

  if (status === 'New' || status === 'Follow-up Due') return true;
  return false;
}

function updateLeadAfterTouch_(sheet, headerMap, rowNum, step, sendMode) {
  const nextStep = step + 1;
  const today = new Date();

  let nextFollowUp = '';
  let nextStatus = sendMode ? 'Sent' : 'Draft Created';

  if (step === 1) {
    nextFollowUp = addDays_(today, 3);
  } else if (step === 2) {
    nextFollowUp = addDays_(today, 4);
  } else {
    nextStatus = sendMode ? 'Sequence Complete' : 'Draft Created - Final';
    nextFollowUp = '';
  }

  sheet.getRange(rowNum, headerMap.Sequence_Step).setValue(nextStep);
  sheet.getRange(rowNum, headerMap.Status).setValue(nextStatus);
  sheet.getRange(rowNum, headerMap.Last_Touch_Date).setValue(formatDate_(today));
  sheet.getRange(rowNum, headerMap.Next_Follow_Up).setValue(nextFollowUp ? formatDate_(nextFollowUp) : '');
}

function buildMessage_(row, step) {
  const contact = row.Contact_Name || 'there';
  const business = row.Business_Name || 'your business';
  const issue1 = row.Issue_1 || 'metadata and intent alignment';
  const issue2 = row.Issue_2 || 'internal linking and structure';
  const quickWin = row.Quick_Win || 'tighten your top service page title and heading around customer intent';
  const offer = row.Primary_Offer || 'SEO audit';
  const targetPage = row.Target_Page || 'https://seowithfaiz.com/resources/seo-audit-playbook.html';

  if (step === 1) {
    return {
      subject: `Quick growth idea for ${business}`,
      body:
`Hi ${contact},

I reviewed ${business} and noticed one issue that may be costing qualified traffic: ${issue1}.

A quick fix you can apply fast is: ${quickWin}.

I run focused ${offer} work for small businesses, and I documented a practical framework here: ${targetPage}

Open to a 15-minute diagnostic call this week?

Regards,
Faiz`
    };
  }

  if (step === 2) {
    return {
      subject: `Re: quick growth idea for ${business}`,
      body:
`Hi ${contact},

Quick follow-up in case this got buried.

The fastest win still looks like: ${quickWin}.
If useful, I can send a short priority list for this month.

Open to a 15-minute diagnostic call this week?

Regards,
Faiz`
    };
  }

  if (step === 3) {
    return {
      subject: `Last note on ${business} SEO`,
      body:
`Hi ${contact},

Last note from my side.

If SEO is not a focus now, no problem. If it is, I can share a one-page action snapshot based on ${issue1} and ${issue2}.

Open to a 15-minute diagnostic call this week?

Regards,
Faiz`
    };
  }

  return null;
}

function writeDailySnapshot_(stats) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const dailySheet = ss.getSheetByName(ENGINE_CONFIG.DAILY_SHEET);
  if (!dailySheet) return;

  const headers = dailySheet.getRange(1, 1, 1, dailySheet.getLastColumn()).getValues()[0];
  const headerMap = {};
  headers.forEach((h, i) => {
    headerMap[String(h).trim()] = i + 1;
  });

  const todayStr = formatDate_(new Date());
  const allRows = dailySheet.getDataRange().getValues();
  let targetRow = -1;

  for (let i = 1; i < allRows.length; i++) {
    if (formatDate_(parseDate_(allRows[i][0])) === todayStr) {
      targetRow = i + 1;
      break;
    }
  }

  if (targetRow === -1) {
    targetRow = dailySheet.getLastRow() + 1;
    dailySheet.getRange(targetRow, 1).setValue(todayStr);
  }

  safeSet_(dailySheet, targetRow, headerMap, 'First_Touches_Sent', stats.firstTouches);
  safeSet_(dailySheet, targetRow, headerMap, 'Followups_Sent', stats.followups);

  const notes = `Drafts:${stats.draftsCreated} | Sent:${stats.emailsSent}`;
  safeSet_(dailySheet, targetRow, headerMap, 'Notes', notes);
}

function safeSet_(sheet, row, headerMap, headerName, value) {
  if (headerMap[headerName]) {
    sheet.getRange(row, headerMap[headerName]).setValue(value);
  }
}

function getLeadSheetAndHeaders_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(ENGINE_CONFIG.LEADS_SHEET);
  if (!sheet) throw new Error(`Missing sheet: ${ENGINE_CONFIG.LEADS_SHEET}`);

  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  const headerMap = {};
  headers.forEach((h, i) => {
    headerMap[String(h).trim()] = i + 1;
  });

  const required = ['Email', 'Sequence_Step', 'Status', 'Last_Touch_Date', 'Next_Follow_Up', 'Outreach_Channel'];
  required.forEach((name) => {
    if (!headerMap[name]) {
      throw new Error(`Missing required header: ${name}`);
    }
  });

  return { sheet, headerMap };
}

function getRows_(sheet, headerMap) {
  const lastRow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();
  if (lastRow < 2) return [];

  const data = sheet.getRange(2, 1, lastRow - 1, lastCol).getValues();
  const headers = Object.keys(headerMap);

  return data.map((rowValues, idx) => {
    const row = { __rowNum: idx + 2 };
    headers.forEach((header) => {
      row[header] = rowValues[headerMap[header] - 1];
    });
    return row;
  });
}

function blankStats_() {
  return {
    firstTouches: 0,
    followups: 0,
    draftsCreated: 0,
    emailsSent: 0
  };
}

function parseDate_(value) {
  if (!value) return null;
  if (Object.prototype.toString.call(value) === '[object Date]' && !isNaN(value)) return value;
  const date = new Date(value);
  return isNaN(date) ? null : date;
}

function formatDate_(date) {
  if (!date) return '';
  return Utilities.formatDate(date, Session.getScriptTimeZone(), 'yyyy-MM-dd');
}

function isSameOrBeforeToday_(date) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const check = new Date(date);
  check.setHours(0, 0, 0, 0);
  return check.getTime() <= today.getTime();
}

function addDays_(date, days) {
  const d = new Date(date);
  d.setDate(d.getDate() + days);
  return d;
}
