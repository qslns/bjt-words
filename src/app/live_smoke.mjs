import { chromium } from 'playwright';
/* 11/13: 컨테이너는 HTTPS_PROXY로만 밖에 나감 → 크로미움에도 같은 프록시 */
const browser = await chromium.launch({ ...(process.env.PW_CHROME ? { executablePath: process.env.PW_CHROME } : {}), ...(process.env.HTTPS_PROXY ? { proxy: { server: process.env.HTTPS_PROXY } } : {}) });
const ctx = await browser.newContext({ viewport: { width: 1180, height: 820 } });
const page = await ctx.newPage(); const errs = [];
page.on('pageerror', e => errs.push(String(e)));
page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource|fonts\.g/.test(m.text())) errs.push(m.text()); });
await page.goto('https://qslns.github.io/bjt-words/?t=' + Date.now());
await page.waitForSelector('#v-home details.gf', { state: 'attached', timeout: 60000 });
const r = await page.evaluate(() => ({ groups: document.querySelectorAll('#v-home details.gf').length, open: document.querySelectorAll('#v-home details.gf[open]').length, kz: !!document.getElementById('v-kanji'), ver: document.querySelector('#v-home .ver').textContent, av: Object.keys(window.__t.AV).length }));
console.log(JSON.stringify(r));
if (await page.locator('#v-home details[data-g="P"]').count()) await page.locator('#v-home details[data-g="P"] > summary').click();   /* 11/13: 1부는 큰 접기 'BJT 단어'(P) 안 */
await page.locator('#v-home details[data-g="p0"] > summary').click();
await page.locator('#v-home details[data-g="p0"] .book').first().click();
await page.waitForSelector('#v-study');
console.log('study opened');
const u = await page.evaluate(() => window.__t.AUD.url('s', 1122, 0));
const st = await page.evaluate(async u => (await fetch(u)).status, u);
console.log('audio url', u, st);
const pos = await page.evaluate(() => [getComputedStyle(document.body).position, !!window.__t.AMEM]); console.log('body', pos);
console.log('errors', errs.length, errs.join(' | '));
await browser.close();
