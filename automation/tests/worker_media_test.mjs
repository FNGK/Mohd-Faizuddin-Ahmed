// Byte-range test for worker.js serveMedia: real video bytes behind a mocked ASSETS.
import fs from "node:fs";
import path from "node:path";
import url from "node:url";

const REPO = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), "../..");
let src = fs.readFileSync(path.join(REPO, "worker.js"), "utf8");
src = src.replace(/import\s*\{\s*EmailMessage\s*\}\s*from\s*['"]cloudflare:email['"];?/, "const EmailMessage = class {};");
const tmp = path.join(process.env.TEMP || ".", "worker_media_stub.mjs");
fs.writeFileSync(tmp, src);
const worker = (await import(url.pathToFileURL(tmp).href)).default;

const FILE = "/assets/video/hero-loop-mobile.mp4";
const bytes = fs.readFileSync(path.join(REPO, FILE));
const env = {
  ASSETS: {
    async fetch(req) {
      const p = new URL(req.url).pathname;
      if (p !== FILE) return new Response("nope", { status: 404 });
      return new Response(bytes, { status: 200, headers: { "Content-Type": "video/mp4", "Content-Length": String(bytes.length) } });
    },
  },
};
const ctx = { waitUntil() {} };
const size = bytes.length;
let pass = 0, fail = 0;
async function check(label, headers, method, expect) {
  const res = await worker.fetch(new Request("https://seowithfaiz.com" + (expect.path || FILE), { method, headers }), env, ctx);
  const body = method === "HEAD" ? new Uint8Array() : new Uint8Array(await res.arrayBuffer());
  const problems = [];
  if (res.status !== expect.status) problems.push(`status ${res.status} != ${expect.status}`);
  if (expect.range && res.headers.get("content-range") !== expect.range) problems.push(`range ${res.headers.get("content-range")} != ${expect.range}`);
  if (expect.len !== undefined && body.length !== expect.len) problems.push(`body ${body.length} != ${expect.len}`);
  if (expect.first !== undefined && body.length && body[0] !== expect.first) problems.push(`first byte ${body[0]} != ${expect.first}`);
  if (expect.status !== 404 && res.headers.get("accept-ranges") !== "bytes") problems.push("missing Accept-Ranges");
  if (problems.length) { fail++; console.log("FAIL", label, problems.join("; ")); } else { pass++; console.log("ok  ", label); }
}

await check("full GET", {}, "GET", { status: 200, len: size });
await check("HEAD", {}, "HEAD", { status: 200 });
await check("Safari probe bytes=0-1", { Range: "bytes=0-1" }, "GET", { status: 206, range: `bytes 0-1/${size}`, len: 2, first: bytes[0] });
await check("open-ended bytes=1000-", { Range: "bytes=1000-" }, "GET", { status: 206, range: `bytes 1000-${size - 1}/${size}`, len: size - 1000, first: bytes[1000] });
await check("suffix bytes=-500", { Range: "bytes=-500" }, "GET", { status: 206, range: `bytes ${size - 500}-${size - 1}/${size}`, len: 500, first: bytes[size - 500] });
await check("end past size", { Range: `bytes=10-${size + 9999}` }, "GET", { status: 206, range: `bytes 10-${size - 1}/${size}`, len: size - 10 });
await check("start past size", { Range: `bytes=${size + 5}-` }, "GET", { status: 416, range: `bytes */${size}` });
await check("multi-range ignored -> full", { Range: "bytes=0-1,5-6" }, "GET", { status: 200, len: size });
await check("missing video 404", {}, "GET", { status: 404, path: "/assets/video/nope.mp4" });
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
