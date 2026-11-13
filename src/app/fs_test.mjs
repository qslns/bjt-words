// 전체화면: 버튼으로만 꺼지고, 다른 방법으로 꺼지면 다음 탭/클릭에서 다시 켜지는지
import { chromium } from 'playwright';
const BASE = process.env.BASE || 'http://127.0.0.1:8765/';
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) { pass++; console.log('  ok  ', m); } else { fail++; console.log('  FAIL', m); } };
const browser = await chromium.launch({ ...(process.env.PW_CHROME ? { executablePath: process.env.PW_CHROME } : {}) }).catch(() => chromium.launch());
const ctx = await browser.newContext({ viewport: { width: 1180, height: 820 }, serviceWorkers: 'block', hasTouch: true });
const page = await ctx.newPage();
const errs = [];
page.on('pageerror', e => errs.push(String(e)));
await page.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
await page.goto(BASE);
await page.waitForTimeout(500);
const isFs = () => page.evaluate(() => !!document.fullscreenElement);
const btn = page.locator('[data-act="full"] >> visible=true').first();
ok(await btn.count() === 1, 'full button visible on home');
await btn.click(); await page.waitForTimeout(400);
ok(await isFs(), 'button turns fullscreen on');
// 시스템이 끈 상황(쓸어내림) 흉내: 버튼이 아니라 직접 exitFullscreen
await page.evaluate(() => document.exitFullscreen()); await page.waitForTimeout(400);
ok(!(await isFs()), 'system exit leaves fullscreen');
// 다음 클릭(버튼 아닌 곳)에서 자동 복귀
await page.locator('h1, .home-h, header').first().click({ force: true }).catch(async () => { await page.mouse.click(600, 400); });
await page.waitForTimeout(400);
ok(await isFs(), 'next click restores fullscreen');
// 탭(터치)으로도 복귀
await page.evaluate(() => document.exitFullscreen()); await page.waitForTimeout(400);
await page.touchscreen.tap(600, 300); await page.waitForTimeout(500);
ok(await isFs(), 'next tap restores fullscreen');
// 버튼으로 끄면 그 뒤엔 안 켜짐
await btn.click(); await page.waitForTimeout(400);
ok(!(await isFs()), 'button turns fullscreen off');
await page.mouse.click(600, 400); await page.waitForTimeout(400);
await page.touchscreen.tap(600, 300); await page.waitForTimeout(400);
ok(!(await isFs()), 'stays off after other clicks/taps');
// 꺼진 상태(want=true)에서 버튼을 누르면 켜짐(꺼지지 않음)
await btn.click(); await page.waitForTimeout(400);
await page.evaluate(() => document.exitFullscreen()); await page.waitForTimeout(400);
await btn.click(); await page.waitForTimeout(500);
ok(await isFs(), 'button after system exit turns it back on (not off)');
ok(errs.length === 0, 'no page errors ' + errs.join(' | '));
console.log(`\n${pass} passed, ${fail} failed`);
await browser.close();
process.exit(fail ? 1 : 0);
