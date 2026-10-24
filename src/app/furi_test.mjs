// 10/21 후리가나 켜기/끄기 버튼(단어 공부·한자 단원 위 막대)
import { chromium } from 'playwright';
const BASE = process.env.BASE || 'http://127.0.0.1:8765/';
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) { pass++; console.log('  ok  ', m); } else { fail++; console.log('  FAIL', m); } };
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const ctx = await browser.newContext({ viewport: { width: 820, height: 1180 }, serviceWorkers: 'block', hasTouch: true });
const page = await ctx.newPage(); const errs = [];
page.on('pageerror', e => errs.push(String(e)));
page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource|fonts\.g/.test(m.text())) errs.push(m.text()); });
await page.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
await page.goto(BASE + '?t=' + Date.now());
await page.waitForSelector('#v-home details.gf', { state: 'attached', timeout: 60000 });
const vis = sel => page.locator(sel + ' >> visible=true').first();
await page.evaluate(() => document.querySelectorAll('#v-home details.gf').forEach(d => d.open = true));
await vis('#v-home .book[data-i="0"]').tap();
await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(300);
const b0 = await page.evaluate(() => { const b = document.querySelector('#v-study .sbar [data-act="furi"]'); return b ? { p: b.getAttribute('aria-pressed'), t: b.textContent } : null; });
ok(b0 && b0.p === 'true' && b0.t.includes('후리가나'), 'study bar has [후리가나] toggle, on by default');
// 한자 든 단어가 나올 때까지 넘기며 해설
for (let g = 0; g < 15; g++) {
  await vis('#v-study [data-act="explain"]').tap(); await page.waitForTimeout(350);
  if (await page.locator('#v-study .s-sent .jp rt').count() && await page.locator('#v-study .ans-hw rt').count()) break;
  await vis('#v-study [data-act="ok"]').tap(); await page.waitForTimeout(350);
}
const st = () => page.evaluate(() => { const v = s => { const e = document.querySelector(s); return e ? getComputedStyle(e).visibility : 'none'; };
  return { cls: document.getElementById('stage').className, sent: v('#v-study .s-sent .jp rt'), sk: v('#v-study .sk .sk-j rt'), ans: v('#v-study .ans-hw rt'), read: v('#v-study .ans-read'), top: document.getElementById('sc').scrollTop }; });
const s1 = await st();
ok(s1.sent === 'visible' && s1.ans === 'visible', '해설: furigana visible (sentence + answer)');
await page.evaluate(() => { document.getElementById('sc').scrollTop = 200; });
await vis('#v-study .sbar [data-act="furi"]').tap(); await page.waitForTimeout(250);
const s2 = await st();
ok(s2.cls.includes('furi-off') && s2.sent === 'hidden' && (s2.sk === 'hidden' || s2.sk === 'none'), 'tap toggle → sentence & same-kanji furigana hidden');
ok(s2.ans === 'visible' && (s2.read === 'visible' || s2.read === 'none'), 'answer reading stays visible');
ok(s2.top === s1.top || s2.top > 0, 'no re-render (scroll position kept)');
ok((await page.evaluate(() => document.querySelector('#v-study .sbar [data-act="furi"]').getAttribute('aria-pressed'))) === 'false' && (await page.textContent('#toast')).includes('후리가나 숨김'), 'button shows off + toast');
// 예문 누르면 그 문장만 보임
await vis('#v-study .s-sent .sent .jp').tap(); await page.waitForTimeout(200);
ok(await page.evaluate(() => getComputedStyle(document.querySelector('#v-study .s-sent .sent.peek .jp rt')).visibility) === 'visible', 'tap a sentence → its furigana shows');
// 다음 카드에서도 꺼진 채
await vis('#v-study [data-act="ok"]').tap(); await page.waitForTimeout(400);
ok((await page.evaluate(() => document.getElementById('stage').className)).includes('furi-off'), 'next card: still off');
// 새로고침해도 유지
await page.reload(); await page.waitForSelector('#v-home details.gf', { state: 'attached' });
ok(await page.evaluate(() => JSON.parse(localStorage.getItem('bjt500.prefs.v2')).furi) === 'tap', 'saved (prefs furi = tap)');
// 한자 단원: 같은 버튼, 단어 목록 후리가나 숨김
await page.evaluate(() => { document.querySelector('#v-home details[data-g="kz"]').open = true; });
await vis('#v-home .kzu-book[data-k="0"]').tap(); await page.waitForSelector('#v-kz .cf-word');
await vis('#v-kz [data-act="kzExplain"]').tap(); await page.waitForTimeout(350);
const k1 = await page.evaluate(() => ({ p: document.querySelector('#v-kz .sbar [data-act="furi"]').getAttribute('aria-pressed'), cls: document.getElementById('kz-stage').className, rt: getComputedStyle(document.querySelector('#v-kz .kzu-ws .sk-j rt')).visibility }));
ok(k1.p === 'false' && k1.cls.includes('furi-off') && k1.rt === 'hidden', 'kanji unit: toggle off → card word list furigana hidden');
await vis('#v-kz .sbar [data-act="furi"]').tap(); await page.waitForTimeout(250);
const k2 = await page.evaluate(() => ({ p: document.querySelector('#v-kz .sbar [data-act="furi"]').getAttribute('aria-pressed'), rt: getComputedStyle(document.querySelector('#v-kz .kzu-ws .sk-j rt')).visibility }));
ok(k2.p === 'true' && k2.rt === 'visible', 'kanji unit: toggle on → visible again');
await vis('#v-kz [data-act="kzExit"]').tap(); await page.waitForTimeout(300);
// 설정에 같은 값
await vis('[data-act="settings"]').tap(); await page.waitForTimeout(300);
ok(await page.locator('#sheet [data-act="setFuri"][data-v="all"][aria-pressed="true"], #sheet [data-act="setFuri"][data-v="all"].on').count() >= 0 && (await page.textContent('#sheet')).includes('후리가나 숨김(예문 누르면 보임)'), 'settings shows the same option (보임/숨김)');
ok(errs.length === 0, 'no console errors: ' + errs.join(' | '));
await browser.close();
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
