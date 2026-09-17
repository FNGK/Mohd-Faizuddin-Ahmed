// Rate-limit tests for worker.js: contact form + CRM login, against a mock D1
// that behaves like the real one (INSERT .. ON CONFLICT .. RETURNING hits).
import fs from "node:fs";
import path from "node:path";
import url from "node:url";

const REPO = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), "../..");
let src = fs.readFileSync(path.join(REPO, "worker.js"), "utf8");
src = src.replace(/import\s*\{\s*EmailMessage\s*\}\s*from\s*['"]cloudflare:email['"];?/, "const EmailMessage = class {};");
const tmp = path.join(process.env.TEMP || ".", "worker_ratelimit_stub.mjs");
fs.writeFileSync(tmp, src);
const worker = (await import(url.pathToFileURL(tmp).href + "?t=" + Date.now())).default;

const KEY = "test-access-key";

function makeD1(opts = {}) {
  const rows = new Map();          // "bucket|ip|window" -> hits
  const log = { creates: 0, deletes: 0, selects: 0 };
  return {
    rows,
    log,
    prepare(sql) {
      let args = [];
      return {
        bind(...a) { args = a; return this; },
        async run() {
          if (/CREATE TABLE IF NOT EXISTS rate_limits/.test(sql)) { log.creates++; if (opts.failCreate) throw new Error("no table"); return {}; }
          if (/DELETE FROM rate_limits/.test(sql)) {
            log.deletes++;
            for (const k of [...rows.keys()]) if (Number(k.split("|")[2]) < args[0]) rows.delete(k);
            return {};
          }
          if (/ALTER TABLE leads/.test(sql)) return {};
          return {};
        },
        async first() {
          if (opts.failAll) throw new Error("D1 down");
          if (/INSERT INTO rate_limits/.test(sql)) {
            const k = args.slice(0, 3).join("|");
            const hits = (rows.get(k) || 0) + 1;
            rows.set(k, hits);
            return opts.noReturning ? {} : { hits };
          }
          if (/SELECT hits FROM rate_limits/.test(sql)) {
            log.selects++;
            const k = args.slice(0, 3).join("|");
            return rows.has(k) ? { hits: rows.get(k) } : null;
          }
          return null;
        },
        async all() { return { results: [] }; },
      };
    },
  };
}

const ctx = { waitUntil(p) { if (p && p.catch) p.catch(() => {}); } };
let pass = 0, fail = 0;
function check(label, cond, extra = "") {
  if (cond) { pass++; console.log("ok   ", label); } else { fail++; console.log("FAIL ", label, extra); }
}

async function post(env, pathname, bodyObj, ip, extraHeaders = {}) {
  const headers = { "Content-Type": "application/json", "CF-Connecting-IP": ip, ...extraHeaders };
  return worker.fetch(new Request("https://seowithfaiz.com" + pathname, { method: "POST", headers, body: JSON.stringify(bodyObj) }), env, ctx);
}

// ── contact form: 8 per 10 min per IP (honeypot payload: no mail is sent) ──
{
  const env = { CRM_DB: makeD1() };
  const codes = [];
  for (let i = 0; i < 10; i++) codes.push((await post(env, "/api/v1/contact", { honeypot: "x" }, "1.1.1.1")).status);
  const expected = [201, 201, 201, 201, 201, 201, 201, 201, 429, 429];
  check("contact: first 8 allowed, then 429", JSON.stringify(codes) === JSON.stringify(expected), codes.join(","));

  const blocked = await post(env, "/api/v1/contact", { honeypot: "x" }, "1.1.1.1");
  const body = await blocked.json();
  const retry = Number(blocked.headers.get("Retry-After"));
  check("contact 429 carries Retry-After within the window", retry > 0 && retry <= 600, String(retry));
  check("contact 429 body has a message the form can show", /try again in a few minutes/i.test(body.message) && body.success === false);
  check("contact 429 is not cacheable", blocked.headers.get("Cache-Control") === "no-store");

  const other = await post(env, "/api/v1/contact", { honeypot: "x" }, "2.2.2.2");
  check("contact: a different IP is unaffected", other.status === 201, String(other.status));
}

// ── CRM login: 8 per 10 min per IP, counted even with the wrong key ──
{
  const env = { CRM_DB: makeD1(), CRM_ACCESS_KEY: KEY };
  const codes = [];
  for (let i = 0; i < 9; i++) codes.push((await post(env, "/api/crm/login", { key: "guess-" + i }, "3.3.3.3")).status);
  check("login: 8 wrong keys give 401, 9th gives 429", JSON.stringify(codes) === JSON.stringify([401, 401, 401, 401, 401, 401, 401, 401, 429]), codes.join(","));

  const blocked = await post(env, "/api/crm/login", { key: KEY }, "3.3.3.3");
  check("login: correct key is also refused while throttled (no bypass)", blocked.status === 429);
  check("login 429 body has an error the CRM UI can show", /too many/i.test((await blocked.json()).error));

  const fresh = await post(env, "/api/crm/login", { key: KEY }, "4.4.4.4");
  const cookie = fresh.headers.get("Set-Cookie") || "";
  check("login: correct key from another IP still signs in", fresh.status === 200 && cookie.includes("swf_crm_s="), String(fresh.status));
}

// ── a signed-in session is never throttled by the login bucket ──
{
  const env = { CRM_DB: makeD1(), CRM_ACCESS_KEY: KEY };
  for (let i = 0; i < 9; i++) await post(env, "/api/crm/login", { key: "guess" }, "5.5.5.5");
  const me = await worker.fetch(new Request("https://seowithfaiz.com/api/crm/me", { headers: { "CF-Connecting-IP": "5.5.5.5", "X-CRM-Key": KEY } }), env, ctx);
  check("throttling the login does not block the CRM API itself", me.status === 200 && (await me.json()).authed === true);
}

// ── window rollover resets the allowance ──
{
  const env = { CRM_DB: makeD1() };
  const realNow = Date.now;
  const base = 1_800_000_000_000; // fixed point in time
  Date.now = () => base;
  for (let i = 0; i < 9; i++) await post(env, "/api/v1/contact", { honeypot: "x" }, "6.6.6.6");
  const blocked = await post(env, "/api/v1/contact", { honeypot: "x" }, "6.6.6.6");
  Date.now = () => base + 600_001; // next 10-minute window
  const afterWindow = await post(env, "/api/v1/contact", { honeypot: "x" }, "6.6.6.6");
  Date.now = realNow;
  check("blocked inside the window, allowed in the next one", blocked.status === 429 && afterWindow.status === 201, `${blocked.status}/${afterWindow.status}`);
}

// ── D1 unavailable: falls back to in-memory counting instead of failing open ──
{
  const env = { CRM_DB: makeD1({ failAll: true }) };
  const codes = [];
  for (let i = 0; i < 10; i++) codes.push((await post(env, "/api/v1/contact", { honeypot: "x" }, "7.7.7.7")).status);
  check("D1 errors: still limits via memory", codes.filter((c) => c === 429).length >= 1, codes.join(","));
  const noD1 = { };
  const codes2 = [];
  for (let i = 0; i < 10; i++) codes2.push((await post(noD1, "/api/v1/contact", { honeypot: "x" }, "8.8.8.8")).status);
  check("no D1 binding at all: still limits via memory", codes2.filter((c) => c === 429).length >= 1, codes2.join(","));
}

// ── D1 without RETURNING support: reads the counter back rather than failing open ──
{
  const d1 = makeD1({ noReturning: true });
  const env = { CRM_DB: d1 };
  const codes = [];
  for (let i = 0; i < 10; i++) codes.push((await post(env, "/api/v1/contact", { honeypot: "x" }, "9.9.9.9")).status);
  check("no RETURNING: limit still enforced", codes.filter((c) => c === 429).length === 2, codes.join(","));
  check("no RETURNING: counter was read back with a SELECT", d1.log.selects > 0);
}

// ── a normal single submission is untouched (mail path reached) ──
{
  const env = {
    CRM_DB: makeD1(),
    CONTACT_EMAIL: { async send() { return; } },
  };
  const res = await post(env, "/api/v1/contact", {
    name: "Test Person", email: "test@example.com", website: "https://example.com",
    region: "USA", goal: "A real inquiry that is long enough to pass validation.",
  }, "10.10.10.10");
  check("a genuine first submission still succeeds", res.status === 201 && (await res.json()).success === true, String(res.status));
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
