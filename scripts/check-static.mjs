#!/usr/bin/env node
// Gate statis landing hermes-monitor-kuliah — jalan di CI (job static-checks).
// 1. Larangan P0 anti-slop (lihat docs/DESIGN.md + ui-anti-slop.md).
// 2. Tag OG/Twitter lengkap + URL absolut ke og-image.png.
// 3. Data jadwal asli: 6 blok hari, 13 baris pelajaran, 21 SKS disebut.
// 4. styles.css tanpa gradient; app.js tanpa placeholder data.
// Usage: node scripts/check-static.mjs
import { readFileSync } from "node:fs";

const html = readFileSync("index.html", "utf8");
const css = readFileSync("styles.css", "utf8");
const js = readFileSync("app.js", "utf8");

let failures = [];
function check(cond, msg) {
  if (!cond) failures.push(msg);
  else console.log("  ok: " + msg);
}

console.log("P0 anti-slop:");
check(!/linear-gradient|radial-gradient|bg-clip-text/i.test(html + css),
  "tanpa gradient / bg-clip-text");
check(!/font-family:\s*["']?(Inter|Roboto)/i.test(css),
  "tanpa Inter/Roboto sebagai font utama");
check(!/Elevate your workflow|Unlock the power|10x faster|99\.9% uptime/i.test(html),
  "tanpa copy generik / statistik vanity");
const emoji = html.match(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/u);
check(!emoji, "tanpa emoji mentah sebagai ikon" + (emoji ? " (" + emoji[0] + ")" : ""));
check(!/rounded-2xl\s+shadow-lg/.test(html), "tanpa rounded-2xl shadow-lg massal");
check(!/lorem ipsum/i.test(html), "tanpa lorem ipsum");

console.log("OG/Twitter:");
for (const tag of [
  'property="og:title"', 'property="og:description"', 'property="og:type"',
  'property="og:url" content="https://hermes-monitor-kuliah.pages.dev/"',
  'property="og:image" content="https://hermes-monitor-kuliah.pages.dev/og-image.png"',
  'name="twitter:card" content="summary_large_image"',
  'name="twitter:title"', 'name="twitter:description"',
  'name="twitter:image" content="https://hermes-monitor-kuliah.pages.dev/og-image.png"',
]) {
  check(html.includes(tag), "tag " + tag);
}

console.log("Data jadwal:");
const days = (html.match(/<article class="day"/g) || []).length;
check(days === 6, `6 blok hari (dapat ${days})`);
const lessons = (html.match(/<li class="lesson"/g) || []).length;
check(lessons === 13, `13 baris pelajaran (dapat ${lessons})`);
check(html.includes("21 SKS") || html.includes("21</dd>"), "21 SKS disebut");
check(html.includes("Sabtu") && html.includes("bentrok 08.00"),
  "bentrok Sabtu 08.00 didokumentasikan");
check(html.includes("contoh"), "status monitor dilabeli contoh dengan jujur");

console.log("CSS/JS:");
check(!/linear-gradient/i.test(css), "styles.css tanpa gradient");
check(/prefers-reduced-motion/.test(css), "prefers-reduced-motion dihormati");
check(/:focus-visible/.test(css), "focus-visible ada");
check(/Asia\/Jakarta/.test(js), "app.js pakai zona Asia/Jakarta");

if (failures.length) {
  console.error("\nFAIL (" + failures.length + "):");
  for (const f of failures) console.error("  - " + f);
  process.exit(1);
}
console.log("\nOK: gate statis lolos");
