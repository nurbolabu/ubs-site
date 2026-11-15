// Measure the rendered height of every positioned element of the English pages at each
// breakpoint. RU/KK pages use these numbers to push content down only by the real growth
// of a translated text.  Usage: node tools/measure.mjs http://localhost:8765/  (needs playwright)
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const require = createRequire(process.env.PLAYWRIGHT_FROM || import.meta.url);
const { chromium } = require('playwright');
const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const base = process.argv[2] || 'http://localhost:8765/';
const slugs = ['index', 'about-ubs', 'ubs-services', 'it-outsourcing', 'warranty-service', 'service-support',
  'delivery', 'information-security', 'our-partners', 'our-clients', 'contacts-ubs'];
const widths = [1440, 1000, 700, 520, 360]; // 1200 / 960 / 640 / 480 / 320 grids
const out = {};
const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
for (const w of widths) {
  const page = await (await browser.newContext({ viewport: { width: w, height: 900 } })).newPage();
  for (const slug of slugs) {
    await page.goto(base + (slug === 'index' ? '' : slug + '/'), { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const data = await page.evaluate(() => {
      const r = {};
      document.querySelectorAll('section.z').forEach(sec => {
        sec.querySelectorAll(':scope > .el').forEach(el => {
          const c = [...el.classList].find(x => /^e\d+$/.test(x));
          if (c) r[sec.id + ' ' + c] = el.offsetParent ? el.offsetHeight : -1;
        });
      });
      return r;
    });
    for (const [k, h] of Object.entries(data)) {
      const key = slug + ' ' + k;
      (out[key] = out[key] || []).push(h);
    }
  }
}
await browser.close();
fs.writeFileSync(path.join(root, 'src/heights.json'), JSON.stringify(out));
console.log('measured', Object.keys(out).length, 'elements');
