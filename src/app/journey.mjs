// 10/17 버그 점검: 아이패드 세로, 손가락 탭(touch)으로 실제 공부 흐름 한 바퀴
import { chromium } from 'playwright';
const URL = process.env.URL || 'http://127.0.0.1:8766/';
const browser = await chromium.launch({ ...(process.env.PW_CHROME ? { executablePath: process.env.PW_CHROME } : {}) });
const ctx = await browser.newContext({ viewport: { width: 820, height: 1180 }, deviceScaleFactor: 1, serviceWorkers: 'block', hasTouch: true, isMobile: true });
const page = await ctx.newPage(); const errs = [], log = [];
page.on('pageerror', e => errs.push(String(e)));
page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource|fonts\.g/.test(m.text())) errs.push(m.text()); });
const ok = (c, m) => log.push((c ? 'ok   ' : 'FAIL ') + m);
const tap = async sel => { const l = page.locator(sel + ' >> visible=true').first(); await l.scrollIntoViewIfNeeded(); await l.tap(); await page.waitForTimeout(380); };
const title = () => page.textContent('#sheet-title');
const sheetOpen = () => page.evaluate(() => !document.getElementById('sheet').hidden);
await page.goto(URL + '?t=' + Date.now());
await page.waitForSelector('#v-home details.gf', { state: 'attached', timeout: 60000 });
// 1) 1부 펼치고 第1章
if (await page.locator('#v-home details[data-g="P"]').count()) await tap('#v-home details[data-g="P"] > summary');   /* 11/13: 1부는 큰 접기 'BJT 단어'(P) 안 */
await tap('#v-home details[data-g="p0"] > summary');
await tap('#v-home details[data-g="p0"] .book[data-i="0"]');
await page.waitForSelector('#v-study .cf-word');
const id0 = await page.evaluate(() => __t.ui.id);
ok(!!id0 || id0 === 0, 'chapter 1 opened by tap, word id ' + id0);
await tap('#v-study [data-act="explain"]');
for (let g = 0; g < 12 && !(await page.locator('#v-study .story .lk-big >> visible=true').count()); g++) { await tap('#v-study [data-act="ok"]'); await tap('#v-study [data-act="explain"]'); }
const lk = await page.locator('#v-study .story .lk-big >> visible=true').count();
ok(lk > 0, 'explain shows 한자 칸 kanji buttons: ' + lk);
if (lk) {
  const c = await page.locator('#v-study .story .lk-big >> visible=true').first().getAttribute('data-c');
  await tap('#v-study .story .lk-big');
  ok(await sheetOpen() && (await title()).includes(c) && await page.locator('#sheet-body .kz-card').count() === 1, 'tap kanji ' + c + ' → kanji card sheet');
  const wbtn = page.locator('#sheet-body .kzu-ws .sk-w >> visible=true');
  ok(await wbtn.count() > 0, 'kanji card has word buttons: ' + await wbtn.count());
  const wid = await wbtn.first().getAttribute('data-id');
  await tap('#sheet-body .kzu-ws .sk-w');
  ok(await page.locator('#sheet-body .ex').count() === 1 && await page.locator('#sheet-back').isVisible(), 'tap word ' + wid + ' → word card sheet (back visible)');
  // 단어 카드 안의 한자 → 또 쌓기
  const lk2 = page.locator('#sheet-body .s-story .lk-big >> visible=true');
  if (await lk2.count()) { const c2 = await lk2.first().getAttribute('data-c'); await tap('#sheet-body .s-story .lk-big'); ok((await title()).includes(c2) && await page.locator('#sheet-body .kz-card').count() === 1, 'stacked again: kanji ' + c2); await tap('#sheet-back'); }
  await tap('#sheet-back');
  ok((await title()).includes(c), 'back → kanji card ' + c);
  await tap('#sheet .sheet-head [data-act="closeSheet"]');
  ok(!(await sheetOpen()), 'close sheet → back to study');
}
// 같은 한자 칸 네모 한자(sk-k)
const skk = page.locator('#v-study .sk .sk-k >> visible=true');
if (await skk.count()) {
  const c = (await skk.first().textContent()).trim().slice(0, 1);
  await skk.first().tap(); await page.waitForTimeout(380);
  ok(await sheetOpen() && await page.locator('#sheet-body .kz-card').count() === 1, '같은 한자 칸 kanji ' + c + ' → kanji card');
  await tap('#sheet .sheet-head [data-act="closeSheet"]');
}
await tap('#v-study [data-act="ok"]');
const id1 = await page.evaluate(() => __t.ui.id);
ok(id1 !== id0, '알고있음 → next word');
await tap('#v-study [data-act="ng"]');
ok(await page.locator('#v-study [data-act="next"] >> visible=true').count() === 1, '모르겠음 → explain + 다음');
await tap('#v-study [data-act="next"]');
ok(await page.evaluate(() => __t.ui.id) !== id1, '다음 → next word');
await tap('[data-act="exit"]');
await page.waitForSelector('#v-home details.gf', { state: 'attached' });
ok(await page.evaluate(() => { const v = document.getElementById('v-home'); return !v.hidden; }), 'exit → home');
const H = await page.evaluate(() => JSON.parse(localStorage.getItem('bjt500.hoedok.v2') || 'null'));
ok(H && H.w && Object.keys(H.w).length >= 2, 'word records saved: ' + (H ? Object.keys(H.w).length : 0));
// 2) 한자 단원
await tap('#v-home details[data-g="kz"] > summary');
await tap('#v-home details[data-g="kz"] .kzu-book[data-k="0"]');
await page.waitForSelector('#v-kz .cf-word');
const k0 = await page.evaluate(() => __t.kui && __t.kui.c);
ok(true, 'kanji unit 漢字1章 opened, first ' + k0);
await tap('#v-kz [data-act="kzExplain"]');
ok(await page.locator('#v-kz .kz-card').count() === 1, '해설 → picture card');
const kw = page.locator('#v-kz .kzu-ws .sk-w >> visible=true');
if (await kw.count()) {
  await tap('#v-kz .kzu-ws .sk-w');
  ok(await sheetOpen() && await page.locator('#sheet-body .ex').count() === 1, 'unit card word → word card sheet');
  await tap('#sheet .sheet-head [data-act="closeSheet"]');
  ok(!(await sheetOpen()) && await page.locator('#v-kz .kz-card').count() === 1, 'close → back to unit card');
}
await tap('#v-kz [data-act="kzOk"]');
await tap('#v-kz [data-act="kzNg"]');
ok(await page.locator('#v-kz [data-act="kzNext"] >> visible=true').count() === 1, 'unit 모르겠음 → 다음');
await tap('#v-kz [data-act="kzNext"]');
await tap('#v-kz [data-act="kzUndo"]');
ok(true, 'undo tapped');
await tap('#v-kz [data-act="kzExit"]');
await page.waitForSelector('#v-home details.gf', { state: 'attached' });
const KR = await page.evaluate(() => JSON.parse(localStorage.getItem('bjt500.kanji.v1') || 'null'));
ok(KR && KR.ch && Object.keys(KR.ch).length === 1, 'kanji record saved separately');
const H2 = await page.evaluate(() => localStorage.getItem('bjt500.hoedok.v2'));
ok(H2 === JSON.stringify(H) || JSON.parse(H2).w && Object.keys(JSON.parse(H2).w).length === Object.keys(H.w).length, 'word records unchanged by kanji unit');
// 3) 홈 다시 그려도 진행중 표시
ok((await page.textContent('#v-home details[data-g="kz"] > summary')).includes('진행중'), 'kanji fold shows 진행중');
// 4) 새로고침 후 이어하기
await page.reload(); await page.waitForSelector('#v-home details.gf', { state: 'attached' });
ok((await page.textContent('#v-home details[data-g="kz"] > summary')).includes('진행중'), 'after reload: still 진행중');
ok(errs.length === 0, 'no console errors: ' + errs.join(' | '));
console.log(log.join('\n'));
await browser.close();
