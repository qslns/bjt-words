// 한자 카드 미리보기 사진(11/14 다시 만듦 — 10월 것은 src 백업에서 빠져 있었음)
// node shot.mjs PAGE.html OUT_PREFIX [WIDTH] → OUT_PREFIX_full.png + 표준출력 마지막 줄에 카드별 [top, height] JSON (preview.py가 잘라 씀)
import { chromium } from 'playwright';
import path from 'path';
const [html, out, width] = process.argv.slice(2);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: +width || 1024, height: 900 }, deviceScaleFactor: 1 });
await page.goto('file://' + path.resolve(html));
await page.evaluate(() => document.fonts && document.fonts.ready);
await page.waitForTimeout(400);
await page.screenshot({ path: out + '_full.png', fullPage: true });
const boxes = await page.evaluate(() => [...document.querySelectorAll('#w > *')].map(e => { const r = e.getBoundingClientRect(); return [Math.round(r.top + scrollY), Math.round(r.height)]; }));
console.log(JSON.stringify(boxes));
await browser.close();
