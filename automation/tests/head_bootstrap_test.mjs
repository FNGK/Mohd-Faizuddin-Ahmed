// The inline head bootstrap (automation/inject_head_bootstrap.py) must behave like
// the old assets/js/canonical-redirect.js: theme before first paint, and GitHub
// Pages visitors sent to the same path on seowithfaiz.com. It must never redirect
// on seowithfaiz.com itself (the old 404.html script would have looped there).
import { execFileSync } from "node:child_process";
import path from "node:path";
import url from "node:url";
import vm from "node:vm";

const ROOT = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), "../..");
const BOOTSTRAP = execFileSync("python", ["-c",
  "import sys; sys.path.insert(0, 'automation'); import inject_head_bootstrap as m; print(m.BOOTSTRAP)"],
  { cwd: ROOT, encoding: "utf8" }).trim();

function run(href, stored, storageThrows = false) {
  const u = new URL(href);
  const attrs = {};
  let redirect = null;
  const ctx = {
    document: { documentElement: { setAttribute: (k, v) => { attrs[k] = v; } } },
    localStorage: { getItem: () => { if (storageThrows) throw new Error("blocked"); return stored; } },
    location: { hostname: u.hostname, pathname: u.pathname, search: u.search, hash: u.hash, href,
                replace: (to) => { redirect = to; } },
  };
  vm.runInNewContext(BOOTSTRAP, ctx);
  return { theme: attrs["data-theme"], redirect };
}

let pass = 0, fail = 0;
function check(label, got, want) {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  ok ? pass++ : fail++;
  console.log(ok ? "ok   " : "FAIL ", label, ok ? "" : `got ${JSON.stringify(got)} want ${JSON.stringify(want)}`);
}

check("site, no saved theme -> dark, no redirect", run("https://seowithfaiz.com/", null), { theme: "dark", redirect: null });
check("site, saved light -> light", run("https://seowithfaiz.com/about/", "light"), { theme: "light", redirect: null });
check("storage blocked -> dark", run("https://seowithfaiz.com/", null, true), { theme: "dark", redirect: null });
check("site 404 path never redirects (no loop)", run("https://seowithfaiz.com/Mohd-Faizuddin-Ahmed/missing", null), { theme: "dark", redirect: null });
check("GitHub Pages page -> same path on site",
  run("https://fngk.github.io/Mohd-Faizuddin-Ahmed/services/local-seo?utm=x#faq", null).redirect,
  "https://seowithfaiz.com/services/local-seo?utm=x#faq");
check("GitHub Pages root (no slash) -> /", run("https://fngk.github.io/Mohd-Faizuddin-Ahmed", null).redirect, "https://seowithfaiz.com/");
check("GitHub Pages root (slash) -> /", run("https://fngk.github.io/Mohd-Faizuddin-Ahmed/", null).redirect, "https://seowithfaiz.com/");
check("GitHub Pages other repo untouched", run("https://fngk.github.io/other-repo/", null).redirect, null);
check("GitHub Pages still applies theme", run("https://fngk.github.io/Mohd-Faizuddin-Ahmed/", "light").theme, "light");

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
