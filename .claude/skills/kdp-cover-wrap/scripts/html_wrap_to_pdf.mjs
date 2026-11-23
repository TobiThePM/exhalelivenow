// html_wrap_to_pdf.mjs — render a cover-wrap HTML artboard to a single-page,
// print-exact PDF for KDP upload.
//
//   node html_wrap_to_pdf.mjs <wrap.html> <out.pdf> <width-in> <height-in>
//   e.g. node html_wrap_to_pdf.mjs wrap-print.html cover.pdf 11.7 8.75
//
// Expects the HTML to follow the print-build pattern (see SKILL.md):
//   - artboard div in 300-DPI pixels (W*300 × H*300)
//   - @media print scales it ×0.32 inside a fixed-size overflow:hidden container
// Why this script instead of bare --print-to-pdf:
//   1. Chrome quantizes fractional-inch paper sizes by ±0.48pt (1/150") however
//      specified; we patch /MediaBox to the exact points afterward. The content
//      box is exact — only the page box is off — so a same-length byte
//      replacement is safe and avoids re-encoding images.
//   2. Waits for webfonts + images before printing.
import { chromium } from '/Users/charliedeist/.npm-global/lib/node_modules/agent-browser/node_modules/playwright-core/index.mjs';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const [html, out, wIn, hIn] = process.argv.slice(2);
if (!html || !out || !wIn || !hIn) {
  console.error('usage: node html_wrap_to_pdf.mjs <wrap.html> <out.pdf> <width-in> <height-in>');
  process.exit(1);
}

const browser = await chromium.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
});
const page = await browser.newPage();
await page.goto('file://' + resolve(html).replace(/ /g, '%20'), { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await page.evaluate(() => Promise.all(
  [...document.images].map(i => i.complete ? null : new Promise(r => { i.onload = i.onerror = r; }))
));
await page.pdf({
  path: out,
  width: `${wIn}in`,
  height: `${hIn}in`,
  margin: { top: 0, bottom: 0, left: 0, right: 0 },
  printBackground: true,
  preferCSSPageSize: false,
});
await browser.close();

// Patch MediaBox to exact points (1in = 72pt).
const wPt = +wIn * 72, hPt = +hIn * 72;
const fmt = (n) => String(Math.round(n * 100) / 100);
let data = readFileSync(out, 'latin1');
const m = data.match(/\/MediaBox\s*\[[^\]]*\]/);
if (!m) throw new Error('no MediaBox found');
let repl = `/MediaBox [0 0 ${fmt(wPt)} ${fmt(hPt)}]`;
const pad = m[0].length - repl.length;
if (pad < 0) throw new Error('replacement longer than original MediaBox');
repl = repl.slice(0, -1) + ' '.repeat(pad) + ']';
writeFileSync(out, data.replace(m[0], repl), 'latin1');
console.log(`wrote ${out} @ ${fmt(wPt)} x ${fmt(hPt)} pts (was ${m[0]})`);
