// 실제 손가락처럼 '조금 움직이며 탭'했을 때 버튼이 눌리는지 (CDP 터치)
import { chromium } from 'playwright';
const BASE = process.env.BASE || 'http://127.0.0.1:8765/';
const browser = await chromium.launch({ ...(process.env.PW_CHROME ? { executablePath: process.env.PW_CHROME } : {}) });
const ctx = await browser.newContext({ viewport: { width: 1180, height: 820 }, serviceWorkers: 'block', hasTouch: true, isMobile: false });
const page = await ctx.newPage();
await page.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
await page.goto(BASE);
await page.waitForSelector('#v-home details.gf', { state: 'attached' });
await page.evaluate(() => document.querySelectorAll('#v-home details.gf').forEach(d => { d.open = true; }));
await page.waitForTimeout(100);
await page.locator('#v-home .book[data-i="0"] >> visible=true').click();
await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(500);
const cdp = await ctx.newCDPSession(page);
async function jitterTap(sel, dx, dy) {
  const b = await page.locator(sel).boundingBox();
  const x = b.x + b.width / 2, y = b.y + b.height / 2;
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] });
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: x + dx, y: y + dy }] });
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  await page.waitForTimeout(450);
}
let okN = 0, N = 6;
for (let k = 0; k < N; k++) {
  const before = await page.evaluate(() => __t.getRun().pos);
  await jitterTap('#v-study [data-act="ok"]', 2, 3);
  const after = await page.evaluate(() => __t.getRun().pos);
  if (after === before + 1) okN++;
}
const hb = await page.evaluate(() => __t.ui.mode);
await jitterTap('#v-study [data-act="explain"]', -2, 2);
const ex = await page.evaluate(() => __t.ui.mode);
console.log(JSON.stringify({ footerTapsWithJitter: okN + '/' + N, explainTap: hb + '→' + ex }));
await browser.close();
