import { chromium } from 'playwright';
const browser = await chromium.launch({ ...(process.env.PW_CHROME ? { executablePath: process.env.PW_CHROME } : {}) });
const res = [];
for (let k = 0; k < 3; k++) {
  const ctx = await browser.newContext({ viewport: { width: 1180, height: 820 }, serviceWorkers: 'block' });
  const page = await ctx.newPage();
  await page.goto('http://127.0.0.1:8766/?t=' + Date.now());
  await page.waitForSelector('#v-home details.gf', { state: 'attached' });
  await page.evaluate(() => document.querySelectorAll('#v-home details.gf').forEach(d => d.open = true));
  await page.locator('#v-home .book[data-i="1"] >> visible=true').click();
  await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(300);
  const r = await page.evaluate(() => { const H = JSON.parse(localStorage.getItem('bjt500.hoedok.v2')); const ch = Object.values(H.ch).find(c => c && c.cur); const o = ch && ch.cur && ch.cur.ord; const D = JSON.parse(document.getElementById('bjt-data').textContent); const ORDER = D.words.filter(w => w.ord != null).sort((a, b) => a.ord - b.ord).map(w => w.id); return o ? { len: o.length, pos: o.indexOf(ORDER[10]), first: o.slice(0, 5), seqFirst: ORDER.slice(0, 5) } : Object.keys(H.ch); });
  res.push(r); await ctx.close();
}
console.log(JSON.stringify(res)); await browser.close();
