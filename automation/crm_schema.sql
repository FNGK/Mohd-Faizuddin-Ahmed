-- SEO With Faiz CRM — D1 schema. Apply with:
--   npx wrangler d1 execute swf-crm --remote --file=automation/crm_schema.sql
CREATE TABLE IF NOT EXISTS leads (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  website TEXT DEFAULT '',
  region TEXT DEFAULT '',
  goal TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'new',
  notes TEXT DEFAULT '',
  ad_consent INTEGER DEFAULT 0,
  an_consent INTEGER DEFAULT 0,
  source TEXT DEFAULT 'contact_form'
);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);

CREATE TABLE IF NOT EXISTS blog_decisions (
  slug TEXT PRIMARY KEY,
  decision TEXT NOT NULL,
  decided_at TEXT NOT NULL,
  applied INTEGER DEFAULT 0
);
