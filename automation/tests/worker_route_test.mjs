// Route test for worker.js — stubs cloudflare:email, mocks ASSETS, and follows
// every redirect with a loop guard. Verifies extensionless slugs 301 to the real
// canonical, real files/dirs still serve, genuine 404s stay 404, and NO loop forms.
import fs from "node:fs";
import path from "node:path";
import url from "node:url";

const REPO = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), "../..");
let src = fs.readFileSync(path.join(REPO, "worker.js"), "utf8");
src = src.replace(/import\s*\{\s*EmailMessage\s*\}\s*from\s*['"]cloudflare:email['"];?/,
                  "const EmailMessage = class {};");
const tmp = path.join(process.env.TEMP || ".", "worker_stub.mjs");
fs.writeFileSync(tmp, src);
const worker = (await import(url.pathToFileURL(tmp).href)).default;

// Files that "exist" on the site (ASSETS returns 200 for these, 404 otherwise).
const EXISTS = new Set([
  "/index.html",
  "/services/index.html",
  "/case-studies/index.html",
  "/case-studies/button-eyes-resort.html",
  "/services/web-design-development.html",
  "/mentions.html",
  "/assets/css/app.min.css",
]);
const env = {
  ASSETS: {
    async fetch(req) {
      const p = new URL(req.url).pathname;
      return new Response("", { status: EXISTS.has(p) ? 200 : 404 });
    },
  },
};
const ctx = { waitUntil() {} };

async function follow(startPath, method = "GET") {
  let cur = "https://seowithfaiz.com" + startPath;
  const chain = [];
  const seen = new Set();
  for (let hop = 0; hop < 8; hop++) {
    if (seen.has(cur)) return { chain, final: "LOOP@" + cur, loop: true };
    seen.add(cur);
    const res = await worker.fetch(new Request(cur, { method }), env, ctx);
    const loc = res.headers.get("location");
    chain.push(res.status + (loc ? " -> " + new URL(loc).pathname : ""));
    if (res.status === 301 || res.status === 302) {
      cur = new URL(loc, cur).href;
      continue;
    }
    return { chain, final: res.status, loop: false };
  }
  return { chain, final: "TOO_MANY_HOPS", loop: true };
}

const cases = [
  // clean canonical URLs serve directly (no redirect)
  ["/case-studies/button-eyes-resort", 200, false],
  ["/services/web-design-development", 200, false],
  ["/mentions", 200, false],
  ["/", 200, false],
  ["/services/", 200, false],
  // legacy .html / index.html -> 301 to clean -> serve
  ["/case-studies/button-eyes-resort.html", 200, false],
  ["/services/web-design-development.html", 200, false],
  ["/mentions.html", 200, false],
  ["/index.html", 200, false],
  ["/services/index.html", 200, false],
  // bare directory (no slash) -> 301 to trailing slash
  ["/services", 200, false],
  ["/case-studies", 200, false],
  // genuine 404 stays 404; static assets unaffected
  ["/does-not-exist", 404, false],
  ["/assets/css/app.min.css", 200, false],
];

let pass = 0, fail = 0;
for (const [p, expFinal, expLoop] of cases) {
  const r = await follow(p);
  const ok = r.final === expFinal && r.loop === expLoop;
  console.log(`${ok ? "PASS" : "FAIL"}  ${p.padEnd(40)} [${r.chain.join(" , ")}]`);
  ok ? pass++ : fail++;
}
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
