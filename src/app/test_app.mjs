// Playwright tests for the BJT app build in ./test (served on BASE)
import { chromium } from 'playwright';
import fs from 'fs';
const BASE = process.env.BASE || 'http://127.0.0.1:8765/';
const data = JSON.parse(fs.readFileSync(process.env.DATA || '/home/claude/work/build/data_final.json', 'utf8'));
const ORDER = data.words.filter(w => w.ord != null).sort((a, b) => a.ord - b.ord).map(w => w.id);
const BORDER = data.words.filter(w => w.bn != null).sort((a, b) => a.bn - b.bn).map(w => w.id);
function genChapters(total) { const list = []; const add = (a, b, kind) => list.push({a, b, kind}); for (let p = 0; p * 500 < total; p++) { const ps = p * 500 + 1, pe = Math.min(total, ps + 499); for (let bs = ps; bs <= pe; bs += 250) { const be = Math.min(pe, bs + 249); for (let e = Math.min(be, bs + 49); ; e = Math.min(be, e + 50)) { add(bs, e, 'step'); if (e >= be) break; } } if (pe - ps + 1 > 250) add(ps, pe, 'review'); } if (total > 500) add(1, total, 'all'); return list; }
const byId = new Map(data.words.map(w => [w.id, w]));
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) { pass++; console.log('  ok  ', m); } else { fail++; console.log('  FAIL', m); } };

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
async function newPage(vp, init) {
  const ctx = await browser.newContext({ viewport: vp, serviceWorkers: 'block' });
  await ctx.addInitScript(() => { try { localStorage.setItem('bjt500.kzunit', '1'); } catch (e) {} });
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource|fonts\.g/.test(m.text())) errs.push(m.text()); });
  await page.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
  if (init) await page.addInitScript(init);
  await page.goto(BASE);
  return { ctx, page, errs };
}
const vis = (page, sel) => page.locator(sel + ' >> visible=true');
/* 10/15: 홈의 큰 묶음은 기본으로 접혀 있음 → 장 카드를 누르기 전에 펼침 */
const openFolds = async page => { await page.evaluate(() => document.querySelectorAll('#v-home details.gf').forEach(d => { d.open = true; })); await page.waitForTimeout(60); };
const seed = (h, s) => `(() => { if (sessionStorage.getItem('seeded')) return; sessionStorage.setItem('seeded','1');
  localStorage.setItem('bjt500.hoedok.v2', ${JSON.stringify(JSON.stringify(h))});${s ? `localStorage.setItem('bjt500.prefs.v2', ${JSON.stringify(JSON.stringify(s))});` : ''} })();`;
const H0 = w => ({ ch: {}, w: w || {}, wr: null, wru: 0, g: { tt: 0, d: {} }, lt: { pos: 0, done: 0, t: 0, u: 1 }, lay: 'v4', rs: 0, u: 1 });

// ---------- 1. home: no light pass, weak words at the top ----------
{
  const { ctx, page, errs } = await newPage({ width: 1180, height: 820 });
  await page.waitForSelector('#v-home .book', { state: 'attached' }); await openFolds(page);
  ok(await page.locator('#v-home .lite').count() === 0 && await page.locator('[data-act="ltGo"]').count() === 0, 'light pass removed from home');
  const order = await page.evaluate(() => [...document.querySelector('#v-home .home').children].map(e => e.className));
  ok(order.indexOf('wk-top') >= 0 && order.indexOf('wk-top') < order.indexOf('resume'), 'weak block is above the chapters: ' + order.slice(0, 4).join(','));
  ok((await page.textContent('#v-home .wk-top')).includes('0개') && (await page.textContent('#v-home .wk-top')).includes('5번'), 'weak block empty state mentions 5');
  ok(await page.locator('#v-home .wk-top [data-act="weakNew"][disabled]').count() === 1, 'weak review disabled when empty');
  const books = await page.locator('#v-home .grp:not(.grp-basic):not(.grp-kz) .book').count();
  ok(books === Math.ceil(ORDER.length / 500) * 11 + 1, 'home renders chapters: ' + books);
  const bbooks = await page.locator('#v-home .grp-basic .book').count();
  ok(bbooks === genChapters(BORDER.length).length, 'home renders basic chapters: ' + bbooks);
  ok((await page.textContent('#v-home .ver')).includes(ORDER.length.toLocaleString()) && (await page.textContent('#v-home .ver')).includes('기본 ' + BORDER.length), 'version line shows word count');
  ok(!(await page.textContent('#v-home .guide')).includes('1회독'), 'guide no longer mentions light pass');
  ok(errs.length === 0, 'no console errors (home): ' + errs.join(' | '));
  await ctx.close();
}

// ---------- 2. chapter: same-kanji block + underline, loop asks shuffle every round ----------
{
  const { ctx, page, errs } = await newPage({ width: 1180, height: 820 });
  await page.waitForSelector('#v-home .book', { state: 'attached' }); await openFolds(page);
  await vis(page, '#v-home .book[data-i="0"]').click();
  await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(350);
  const first = await page.evaluate(() => __t.ui.id);
  await vis(page, '[data-act="explain"]').click(); await page.waitForTimeout(380);
  const w = byId.get(first);
  ok(await page.locator('#v-study .ans-mn').count() === 0, 'mnemonic line removed');
  const relN = [...new Set(w.kj)].reduce((n, c) => n + ((data.kanji[c] && data.kanji[c].u.filter(i => i !== w.id).length) || 0), 0);
  if (relN) {
    const skIds = await page.$$eval('#v-study .sk .sk-w:not(.more)', els => els.map(e => +e.dataset.id));
    ok(skIds.length > 0 && !skIds.includes(first) && new Set(skIds).size === skIds.length, 'same-kanji words under meaning (no self, no dupes): ' + skIds.length);
    const fs = await page.$eval('#v-study .sk .sk-j', el => parseFloat(getComputedStyle(el).fontSize));
    ok(fs >= 30, 'same-kanji words are big (' + fs + 'px)');
    ok(await page.locator('#v-study .sk .sk-j rt').count() > 0, 'same-kanji words have furigana');
  }
  if (w.st && w.st.includes('→')) ok(await page.locator('#v-study .s-story .st-w u.em').count() === 1, 'story conclusion underlined');
  if (w.p && w.p.includes('「')) ok(await page.locator('#v-study .s-pt u.em').count() >= 1, 'BJT point 「」 underlined');
  await vis(page, '[data-act="ng"]').click(); await page.waitForTimeout(380);   // 첫 단어 모름
  for (let i = 0; i < 80; i++) {
    if (await page.locator('#modal:not([hidden])').count()) break;
    const okb = page.locator('#v-study [data-act="ok"] >> visible=true');
    if (await okb.count()) { await okb.click(); await page.waitForTimeout(320); } else break;
  }
  ok(await page.locator('#modal:not([hidden]) [data-act="loopGo"]').count() === 2, 'loop dialog asks: shuffle / in order');
  ok((await page.textContent('#modal .dlg')).includes('순서를 섞을까요'), 'loop dialog question text');
  await vis(page, '#modal [data-act="loopGo"][data-v="0"]').click(); await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(350);
  ok((await page.evaluate(() => __t.getRun().shuf)) === false, 'in-order chosen');
  ok(await page.evaluate(() => __t.ui.id) === first, 'round 1 shows the missed word');
  await vis(page, '[data-act="ng"]').click(); await page.waitForTimeout(380);
  if (relN) ok(await page.locator('#v-study .sk').count() === 1, 'same-kanji block also on the unknown screen');
  await vis(page, '[data-act="next"]').click(); await page.waitForTimeout(380);
  ok(await page.locator('#modal:not([hidden]) [data-act="roundGo"]').count() === 2, 'round 2 asks shuffle again');
  ok((await page.textContent('#modal .dlg h2')).includes('1개'), 'round dialog shows remaining count');
  await vis(page, '#modal [data-act="roundGo"][data-v="1"]').click(); await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(350);
  ok((await page.evaluate(() => [__t.getRun().shuf, __t.getRun().round])).join() === 'true,2', 'shuffle chosen for round 2');
  ok((await page.textContent('#toast')).includes('섞어서'), 'toast says shuffled');
  // reload while dialog would show: answer ng again, then reload -> dialog again
  await vis(page, '[data-act="ng"]').click(); await page.waitForTimeout(380);
  await vis(page, '[data-act="next"]').click(); await page.waitForTimeout(380);
  await page.reload(); await page.waitForSelector('#v-home .book', { state: 'attached' }); await openFolds(page);
  await vis(page, '[data-act="resume"]').click(); await page.waitForTimeout(400);
  ok(await page.locator('#modal:not([hidden]) [data-act="roundGo"]').count() === 2, 'after reload the round question comes back');
  await vis(page, '#modal [data-act="roundGo"][data-v="0"]').click(); await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(350);
  await vis(page, '[data-act="ok"]').click(); await page.waitForTimeout(380);
  ok(await page.locator('#modal:not([hidden]) .sum').count() === 1, 'summary after all known');
  const m = await page.evaluate(id => JSON.parse(localStorage.getItem('bjt500.hoedok.v2')).w[id].m, first);
  ok(m === 3, 'miss count accumulates (3)');
  ok(await page.evaluate(id => __t.isWeak(id), first) === false, '3 misses is not weak yet (threshold 5)');
  ok(errs.length === 0, 'no console errors (study): ' + errs.join(' | '));
  await ctx.close();
}

// ---------- 2b. cumulative across chapters: 4 before + 1 now = weak ----------
{
  const target = ORDER[10];
  const { ctx, page, errs } = await newPage({ width: 1180, height: 820 }, seed(H0({ [target]: { n: 2, m: 4, l: 0, t: 1, pin: 0, rm: -1, u: 1 } })));
  await page.waitForSelector('#v-home .book', { state: 'attached' }); await openFolds(page);
  ok((await page.textContent('#v-home .wk-top b')).includes('0개'), '4 misses: not weak yet');
  await vis(page, '#v-home .book[data-i="1"]').click();   // 1–100
  await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(350);
  for (let i = 0; i < 110; i++) {
    if (await page.locator('#modal:not([hidden])').count()) break;
    const id = await page.evaluate(() => __t.ui.id);
    if (id === target) { await vis(page, '[data-act="ng"]').click(); await page.waitForTimeout(330); await vis(page, '[data-act="next"]').click(); await page.waitForTimeout(330); break; }
    await vis(page, '#v-study [data-act="ok"]').click(); await page.waitForTimeout(300);
  }
  ok(await page.evaluate(id => __t.isWeak(id), target) === true, '5th miss (cumulative) makes it weak');
  /* 섞인 순서에서 target이 마지막 카드였으면 라운드 질문 창이 떠 있음(1/100) → 닫고 나가기 */
  if (await page.locator('#modal:not([hidden])').count()) { await vis(page, '#modal [data-act="loopGo"][data-v="0"]').click(); await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(300); }
  await vis(page, '[data-act="exit"]').click(); await page.waitForSelector('#v-home .wk-top'); await openFolds(page);
  ok((await page.textContent('#v-home .wk-top b')).includes('1개'), 'home weak count 1');
  ok(errs.length === 0, 'no console errors (cumulative): ' + errs.join(' | '));
  await ctx.close();
}

// ---------- 2c. same-kanji: +N more, tap opens the word ----------
{
  const cands = data.words.filter(w => w.ord != null).sort((a, b) => a.ord - b.ord).filter(w => w.kj.length === 1 && data.kanji[w.kj[0]].u.length > 8);
  const w = cands[0];
  const { ctx, page, errs } = await newPage({ width: 1180, height: 820 }, seed(H0({ [w.id]: { n: 1, m: 6, l: 0, t: 1, pin: 0, rm: -1, u: 1 } })));
  await page.waitForSelector('#v-home .wk-top'); await openFolds(page);
  await vis(page, '#v-home .wk-top [data-act="weakNew"]').click(); await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(350);
  await vis(page, '[data-act="explain"]').click(); await page.waitForTimeout(400);
  const nVis = await page.locator('#v-study .sk-w >> visible=true').count();
  ok(nVis === 6, w.w + ': 6 words shown first');
  const skIds = await page.$$eval('#v-study .sk .sk-w', els => els.map(e => +e.dataset.id));
  ok(!skIds.includes(w.id) && new Set(skIds).size === skIds.length, 'no self, no duplicates');
  const fs = await page.$eval('#v-study .sk .sk-j', el => parseFloat(getComputedStyle(el).fontSize));
  ok(fs >= 30, 'same-kanji words are big (' + fs + 'px)');
  ok(await page.locator('#v-study .sk .sk-j rt').count() > 0, 'same-kanji words have furigana');
  await page.screenshot({ path: '/home/claude/work/app/shot_sk_1180.png' });
  const total = data.kanji[w.kj[0]].u.filter(i => i !== w.id).length;
  ok((await page.textContent('#v-study .sk-more')).includes('+' + (total - 6)), 'more button shows +' + (total - 6));
  await vis(page, '#v-study .sk-more').click(); await page.waitForTimeout(150);
  ok(await page.locator('#v-study .sk-w >> visible=true').count() === total, 'more reveals all ' + total);
  const tid = +(await page.locator('#v-study .sk-w').first().getAttribute('data-id'));
  const firstNo = await page.$$eval('#v-study .sk-w', els => els.map(e => +e.dataset.id));
  const uu = data.kanji[w.kj[0]].u.filter(i => i !== w.id && byId.has(i));
  const anc = uu.filter(i => byId.get(i).bn != null).sort((a, b) => byId.get(a).bn - byId.get(b).bn).slice(0, 2);
  const exp = anc.concat(uu.filter(i => byId.get(i).ord != null && !anc.includes(i)).sort((a, b) => byId.get(a).ord - byId.get(b).ord), uu.filter(i => byId.get(i).ord == null && !anc.includes(i)).sort((a, b) => byId.get(a).bn - byId.get(b).bn));
  ok(firstNo.join() === exp.join(), 'ordered: basic 2 → 1500 by number → other basic (none seen)');
  await vis(page, '#v-study .sk-w').first().click(); await page.waitForTimeout(400);
  ok((await page.textContent('#sheet')).includes(byId.get(tid).m.slice(0, 2)), 'tap opens the related word: ' + byId.get(tid).w);
  ok(errs.length === 0, 'no console errors (same-kanji): ' + errs.join(' | '));
  await ctx.close();
}


// ---------- 2d. 0부 기본: basic chapter, card labels, list filter, weak, kanji row ----------
{
  const bOnly = BORDER.filter(id => byId.get(id).ord == null), shared = BORDER.filter(id => byId.get(id).ord != null);
  const { ctx, page, errs } = await newPage({ width: 1180, height: 820 }, seed(H0({ [bOnly[0]]: { n: 1, m: 0, l: 0, t: 1, pin: 1, rm: -1, u: 1 } })));
  await page.waitForSelector('#v-home .grp-basic'); await openFolds(page);
  ok((await page.textContent('#v-home .grp-basic .grp-h')).includes('0부 · 기본'), 'home shows 0부 · 기본');
  const hk = await page.evaluate(() => [...document.querySelector('#v-home .home').children].map(e => e.className));
  ok(hk.indexOf('grp grp-basic') > hk.indexOf('resume') && hk.indexOf('grp grp-basic') < hk.findIndex(c => c === 'grp'), 'basic section sits above 1부: ' + hk.slice(0, 5).join(','));
  ok((await page.textContent('#v-home .resume')).includes('基本1章'), 'next suggestion is 基本1章');
  ok((await page.textContent('#v-home .wk-top b')).includes('1개'), 'pinned basic word counts as weak');
  const bi = await page.getAttribute('#v-home .grp-basic .book >> nth=0', 'data-i');
  await vis(page, '#v-home .grp-basic .book').first().click(); await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(350);
  ok((await page.textContent('#v-study .sb-t')).includes('基本1章') && (await page.textContent('#v-study .sb-t')).includes('기본 1–50'), 'study bar names basic chapter');
  const run = await page.evaluate(() => __t.getRun().ord);
  ok(run.length === 50 && run.every(id => BORDER.slice(0, 50).includes(id)), 'basic chapter 1 has basic 1–50');
  const top = await page.textContent('#v-study .cf-top');
  const cur = await page.evaluate(() => __t.getRun().ord[__t.getRun().pos]);
  const cw = byId.get(cur);
  ok(cw.ord == null ? top.includes('기본 ' + cw.bn) && top.includes('기본') : top.includes('No.') && top.includes('기본 ' + cw.bn), 'card top shows basic number: ' + top.trim());
  await vis(page, '[data-act="explain"]').click(); await page.waitForTimeout(400);
  const html = await page.innerHTML('#v-study');
  ok(!/undefined|NaN/.test(html), 'no undefined/NaN in basic card');
  ok(await page.locator('#v-study .sent').count() === cw.e.length, 'basic card shows all ' + cw.e.length + ' sentences');
  ok(!cw.st || (await page.locator('#v-study .st-w').count()) > 0, 'basic card shows 이야기 line');
  ok(!cw.p || (await page.locator('#v-study .s-pt').count()) > 0, 'basic card shows BJT 포인트');
  ok(!(cw.pr && cw.pr.length) || (await page.locator('#v-study .s-pair .pchip').count()) === cw.pr.filter(i => byId.has(i)).length, 'basic card shows 헷갈리는 짝 chips');
  ok(errs.length === 0, 'no console errors (basic): ' + errs.join(' | '));
  await vis(page, '[data-act="exit"]').click(); await page.waitForSelector('#v-home .grp-basic'); await openFolds(page);
  // list: 기본 filter
  await vis(page, '#v-home [data-act="browse"]').click(); await page.waitForSelector('#blist');
  await vis(page, '[data-act="bf"][data-grp="tier"][data-v="K"]').click(); await page.waitForTimeout(300);
  ok(await page.locator('#blist > li').count() === BORDER.length, 'list filter 기본 shows ' + BORDER.length);
  const nums = await page.$$eval('#blist .num', els => els.slice(0, 400).map(e => e.textContent));
  ok(!nums.some(t => /undefined|NaN/.test(t)) && nums.some(t => t.startsWith('기')), 'list numbers ok for basic-only words');
  await page.fill('#bq', byId.get(bOnly[0]).m.split(/[·(]/)[0]); await page.waitForTimeout(300);
  ok(await page.locator('#blist [data-id="' + bOnly[0] + '"]').count() === 1, 'search finds basic word by meaning');
  ok(errs.length === 0, 'no console errors (basic list): ' + errs.join(' | '));
  await ctx.close();
}
// ---------- 2e. basic progress survives adding more basic words (chapter keys are per chapter content) ----------
{
  const { ctx, page } = await newPage({ width: 1180, height: 820 });
  await page.waitForSelector('#v-home .grp-basic'); await openFolds(page);
  const k = await page.evaluate(() => { const c = __t.CHAPTERS.find(c => c.basic); return c.key; });
  ok(/^B:[0-9a-z]+\.50:1-50:step$/.test(k), 'basic chapter key format: ' + k);
  await ctx.close();
  const init = seed({ ch: { 999: { n: 2, cur: null, t: 10, last: null, u: 5, k } }, w: {}, wr: null, wru: 0, g: { tt: 1, d: {} }, lt: { pos: 0, done: 0, t: 0, u: 1 }, lay: 'v4', rs: 0, u: 1 });
  const p2 = await newPage({ width: 1180, height: 820 }, init);
  await p2.page.waitForSelector('#v-home .grp-basic'); await openFolds(p2.page);
  const n = await p2.page.evaluate(() => { const c = __t.CHAPTERS.find(c => c.basic); return __t.H.ch[c.i] && __t.H.ch[c.i].n; });
  ok(n === 2, 'basic chapter progress found by key');
  ok((await p2.page.textContent('#v-home .grp-basic .book')).includes('3회독'), 'basic book shows next pass');
  await p2.ctx.close();
}
// ---------- 3. migration: old prefs (wkN 2) -> 5, records kept ----------
{
  const firstOld = ORDER.find(id => id < 500);
  const init = `(() => { if (sessionStorage.getItem('seeded')) return; sessionStorage.setItem('seeded','1');
    localStorage.setItem('bjt500.hoedok.v2', JSON.stringify({ch:{0:{n:2,cur:null,t:5000,last:null,u:1}}, w:{${firstOld}:{n:3,m:2,l:0,t:1,pin:0,rm:-1,u:1}}, wr:null, wru:0, g:{tt:123000,d:{}}, rs:0, u:1}));
    localStorage.setItem('bjt500.prefs.v2', JSON.stringify({auto:true,rate:1,sent:true,shuf:false,wkN:2,furi:'all',tr:'show',kp:false,exam:'2026-10-07',u:1})); })();`;
  const { ctx, page, errs } = await newPage({ width: 1180, height: 820 }, init);
  await page.waitForSelector('#v-home .book', { state: 'attached' }); await openFolds(page);
  ok(await page.evaluate(() => __t.S.wkN) === 5, 'old wkN 2 becomes 5');
  const st = await page.evaluate(() => ({ h: JSON.parse(localStorage.getItem('bjt500.hoedok.v2')), s: JSON.parse(localStorage.getItem('bjt500.prefs.v2')) }));
  ok(st.h.w[firstOld] && st.h.w[firstOld].m === 2, 'word records kept');
  ok(st.h.g.tt === 123000, 'study time kept');
  ok(st.s.exam === '2026-10-22', 'exam date moved to 10-22');
  ok((await page.textContent('#v-home .wk-top b')).includes('0개'), '2 misses no longer weak');
  // settings: choose 3, persists
  await vis(page, '[data-act="settings"]').click();
  ok(await page.locator('#sheet [data-act="setWk"]').count() === 3, 'threshold options 3/5/7');
  await vis(page, '#sheet [data-act="setWk"][data-v="3"]').click(); await page.waitForTimeout(200);
  await page.reload(); await page.waitForSelector('#v-home .book', { state: 'attached' }); await openFolds(page);
  ok(await page.evaluate(() => __t.S.wkN) === 3, 'chosen 3 persists after reload');
  // export → reset → import
  await vis(page, '[data-act="settings"]').click();
  await vis(page, '[data-act="exportOpen"]').click();
  await page.waitForSelector('#code-out');
  const code = await page.inputValue('#code-out');
  ok(/^BJT500Z?\./.test(code), 'export code made');
  await vis(page, '#modal [data-act="cfmNo"]').click();
  await page.evaluate(() => { localStorage.removeItem('bjt500.hoedok.v2'); });
  await page.reload(); await page.waitForSelector('#v-home .book', { state: 'attached' }); await openFolds(page);
  await vis(page, '[data-act="settings"]').click();
  await vis(page, '[data-act="importOpen"]').click();
  await page.fill('#code-in', code);
  await vis(page, '[data-act="importGo"]').click(); await page.waitForTimeout(400);
  const h2 = await page.evaluate(() => JSON.parse(localStorage.getItem('bjt500.hoedok.v2')));
  ok(h2.w[firstOld] && h2.w[firstOld].m === 2, 'import restores word records');
  ok(errs.length === 0, 'no console errors (migration): ' + errs.join(' | '));
  await ctx.close();
}
// ---------- 3c. progress saved by the deployed build survives ----------
{
  const init = seed({ ch: { 0: { n: 3, cur: null, t: 5000, last: null, u: 5, k: 'zkf6ci.500:1-50:step' }, 11: { n: 1, cur: null, t: 100, last: null, u: 6, k: '1g6pezw.500:501-550:step' } }, w: {}, wr: null, wru: 0, g: { tt: 1000, d: {} }, lt: { pos: 0, done: 0, t: 0, u: 7 }, lay: 'v4', rs: 0, u: 1 });
  const { ctx, page, errs } = await newPage({ width: 1180, height: 820 }, init);
  await page.waitForSelector('#v-home .book', { state: 'attached' }); await openFolds(page);
  const r = await page.evaluate(() => { const H = JSON.parse(localStorage.getItem('bjt500.hoedok.v2')); return { c0: H.ch[0] && H.ch[0].n, c11: H.ch[11] && H.ch[11].n }; });
  ok(r.c0 === 3 && r.c11 === 1, 'part 1·2 chapter states kept');
  ok(errs.length === 0, 'no console errors (keep): ' + errs.join(' | '));
  await ctx.close();
}

// ---------- 5. weak words: order by misses, select delete + delete all + undo ----------
{
  const pinIds = ORDER.slice(0, 6);
  const wobj = Object.fromEntries(pinIds.map((id, k) => [id, { n: 3, m: 5 + (k % 3), l: 0, t: 1, pin: 0, rm: -1, u: 1 }]));
  const { ctx, page, errs } = await newPage({ width: 1180, height: 820 }, seed(H0(wobj)));
  await page.waitForSelector('#v-home .wk-top'); await openFolds(page);
  ok((await page.textContent('#v-home .wk-top b')).includes('6개'), 'home weak count 6');
  ok((await page.textContent('#v-home .wk-top .wk-h span')).includes('×7'), 'home shows most-missed first');
  await vis(page, '#v-home .wk-top [data-act="weakNew"]').click(); await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(350);
  const ord = await page.evaluate(() => __t.getRun().ord.map(id => __t.H.w[id].m));
  ok(ord.join() === ord.slice().sort((a, b) => b - a).join(), 'weak review goes most-missed first: ' + ord.join(','));
  ok((await page.textContent('#v-study .sb-t span')).includes('많이 틀린 순'), 'weak review subtitle');
  await vis(page, '[data-act="exit"]').click(); await page.waitForSelector('#v-home .wk-top'); await openFolds(page);
  ok((await page.textContent('#v-home .wk-top [data-act="weakGo"]')).includes('이어서'), 'home offers resume of weak review');
  await vis(page, '#v-home .wk-top [data-act="weakView"]').click(); await page.waitForSelector('#wlist');
  ok(await page.locator('#wlist > li').count() === 6, 'weak list has 6');
  await vis(page, '[data-act="wselOn"]').click(); await page.waitForSelector('#wsel-n');
  const rows = page.locator('#wlist [data-act="wpick"]');
  await rows.nth(0).click(); await rows.nth(1).click(); await page.waitForTimeout(100);
  ok((await page.textContent('#wsel-n')).startsWith('2'), 'two picked');
  await vis(page, '[data-act="wdelSel"]').click(); await vis(page, '[data-act="cfmOk"]').click(); await page.waitForTimeout(200);
  ok(await page.locator('#wlist > li').count() === 4, 'selected delete removes 2');
  await vis(page, '[data-act="toastAct"]').click(); await page.waitForTimeout(200);
  ok(await page.locator('#wlist > li').count() === 6, 'undo restores 2');
  await vis(page, '[data-act="wdelAll"]').click(); await vis(page, '[data-act="cfmOk"]').click(); await page.waitForTimeout(200);
  ok(await page.locator('#wlist > li').count() === 0 && await page.locator('#v-weak .empty-note').count() === 1, 'delete all empties the list');
  const h = await page.evaluate(() => JSON.parse(localStorage.getItem('bjt500.hoedok.v2')));
  ok(Object.values(h.w).every(x => x.m >= 5) && h.wr === null, 'miss records kept, weak run cleared');
  await vis(page, '[data-act="toastAct"]').click(); await page.waitForTimeout(200);
  ok(await page.locator('#wlist > li').count() === 6, 'undo after delete all restores');
  ok(errs.length === 0, 'no console errors (weak): ' + errs.join(' | '));
  await ctx.close();
}
// ---------- 6. minimal look + overflow with the longest headword ----------
for (const vp of [{ width: 1180, height: 820 }, { width: 390, height: 844 }, { width: 820, height: 1180 }]) {
  const longest = data.words.slice().sort((a, b) => [...b.w].length - [...a.w].length)[0];
  const h = H0({ [longest.id]: { n: 1, m: 6, l: 0, t: 1, pin: 0, rm: -1, u: 1 } });
  const { ctx, page, errs } = await newPage(vp, seed(h));
  await page.waitForSelector('#v-home .wk-top'); await openFolds(page);
  const c = await page.evaluate(() => { const g = (sel, prop) => { const el = document.querySelector(sel); return el ? getComputedStyle(el)[prop] : null; }; return [g('#v-home .book', 'backgroundColor'), getComputedStyle(document.body).backgroundColor, g('#v-home .wk-top', 'borderTopColor')]; });
  const gray = v => { const m = /rgba?\((\d+), (\d+), (\d+)/.exec(v || ''); return m && m[1] === m[2] && m[2] === m[3]; };
  ok(c.every(gray), 'home colors neutral ' + vp.width + ': ' + c.join(' | '));
  let over = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  ok(!over, `home no horizontal overflow ${vp.width}`);
  await page.screenshot({ path: `/home/claude/work/app/shot_home_${vp.width}.png` });
  await vis(page, '#v-home .wk-top [data-act="weakNew"]').click(); await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(350);
  await vis(page, '[data-act="explain"]').click(); await page.waitForTimeout(400);
  over = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1 || [...document.querySelectorAll('#v-study .ans-hw, #v-study .story, #v-study .ans-mn')].some(el => el.scrollWidth > el.clientWidth + 2));
  ok(!over, `explain no horizontal overflow ${vp.width}x${vp.height} for ${longest.w}`);
  await page.screenshot({ path: `/home/claude/work/app/shot_explain_${vp.width}.png`, fullPage: false });
  ok(errs.length === 0, 'no console errors (layout ' + vp.width + '): ' + errs.join(' | '));
  await ctx.close();
}
// ---------- 7. re-recorded audio: ?v= hash on basic audio, stale cached copies pruned once ----------
{
  const { ctx, page, errs } = await newPage({ width: 1180, height: 820 });
  await page.waitForSelector('#v-home .grp-basic'); await openFolds(page);
  const r = await page.evaluate(async () => {
    const t = window.__t, ids = Object.keys(t.AV);
    const bk = ids.find(k => k.startsWith('w/')), bid = Number(bk.slice(2));
    const mid = [...Array(1500).keys()].find(i => !t.AV['w/' + i]);   // 10/22: 다시 녹음한 본편 단어(w/1 등)는 ?v=가 붙으므로 안 바뀐 본편 단어로
    const out = { on: t.AUD.on, n: ids.length, avh: t.AVH, bu: t.AUD.url('w', bid), main: t.AUD.url('w', mid), want: t.AV[bk], mid };
    const c = await caches.open('bjt-audio-v1');
    const base = new URL('audio/w/' + bid + '.mp3', location.href).href, mainU = new URL('audio/w/' + mid + '.mp3', location.href).href;
    await c.put(base, new Response('old'));
    await c.put(base + '?v=deadbeef', new Response('older'));
    await c.put(out.bu, new Response('new'));
    await c.put(mainU, new Response('main'));
    localStorage.removeItem('bjt500.avh');
    out.pruned = await t.audioPrune();
    out.left = (await c.keys()).map(q => q.url.replace(location.origin, ''));
    out.flag = localStorage.getItem('bjt500.avh');
    out.again = await t.audioPrune();
    return out;
  });
  ok(r.on && r.n > 1000 && /^[0-9a-f]{8}$/.test(r.avh), 'audio versions present: ' + r.n + ' ' + r.avh);
  ok(r.bu.endsWith('?v=' + r.want) && !r.main.includes('?'), 'basic audio url has ?v=, main audio url unchanged');
  ok(r.pruned === 2 && r.left.length === 2 && r.left.some(u => u.includes('?v=' + r.want)) && r.left.some(u => u.endsWith('/audio/w/' + r.mid + '.mp3')), 'prune removes stale basic copies only: ' + r.left.join(' '));
  ok(r.flag === r.avh && r.again === 0, 'prune runs once per audio version');
  ok(errs.length === 0, 'no console errors (audio versions): ' + errs.join(' | '));
  await ctx.close();
}
// ---------- 8. 10/15: 홈 큰 묶음 접힘 · (10/16) 한자 묶음 · 단어 카드 한자칸(훈음 + 장면 한 줄, 한자·부수 풀이 없음) ----------
{
  const KATA = /[ァ-ヺ]/;
  const { ctx, page, errs } = await newPage({ width: 1180, height: 820 });
  await page.waitForSelector('#v-home details.gf', { state: 'attached' });
  ok(await page.locator('#v-home details.gf').count() === 6, 'home has 6 folding groups (기본 2 · 1–3부 · 한자)');
  ok(await page.locator('#v-home details.gf[open]').count() === 0, 'all groups folded by default');
  ok(await page.locator('#v-home .book >> visible=true').count() === 2, 'only the two 총정리 books visible when folded');
  ok(await page.locator('#v-kanji').count() === 0 && await page.locator('#v-home .grp-kz details[data-g="kz"]').count() === 1, 'kanji unit is one folding group (key kz) on home');
  const sumTxt = await page.textContent('#v-home .grp:not(.grp-basic) details.gf summary');
  ok(sumTxt.includes('1부') && sumTxt.includes('No.1–500') && sumTxt.includes('끝낸 장 0/11'), 'part summary shows range + progress: ' + sumTxt.trim());
  await page.locator('#v-home details[data-g="p0"] > summary').click(); await page.waitForTimeout(150);
  ok(await page.locator('#v-home details[data-g="p0"] .book >> visible=true').count() === 11, 'tap opens 1부 (11 books)');
  await vis(page, '#v-home [data-act="browse"]').click(); await page.waitForSelector('#blist');
  await page.keyboard.press('Escape'); await page.waitForSelector('#v-home details.gf', { state: 'attached' }); await page.waitForTimeout(100);
  ok(await page.locator('#v-home details[data-g="p0"][open]').count() === 1 && await page.locator('#v-home details.gf[open]').count() === 1, 'opened group stays open after home re-render, others stay folded');
  await page.reload(); await page.waitForSelector('#v-home details.gf', { state: 'attached' }); await openFolds(page);
  ok(await page.locator('#v-home details.gf[open]').count() === 6, 'helper can open all groups');
  // 10/16 단어 카드: 칸 이름 '한자'(한자 없는 가나 단어는 '이야기'), 한자 줄 = [네모 한자 버튼] 훈음 + 이 단어 읽기 / 카드 장면 한 줄(카드 없는 한자는 옛 구성 + 풀이), 한자·부수 풀이 없음
  const wr = await page.evaluate(() => {
    const bad = []; const t = window.__t; let rows = 0, cardRows = 0, oldRows = 0; const KATA = /[ァ-ヺ]/;
    const D = JSON.parse(document.getElementById('bjt-data').textContent), KJ = D.kanji, KC = D.kc || {};
    if (D.kz) bad.push('data.kz still there');
    if (!Array.isArray(D.kzo) || D.kzo.length !== Object.keys(KJ).length) bad.push('data.kzo ' + (D.kzo || []).length);
    for (const w of D.words) {
      const st = t.storyHTML(w, 's-story'), ex = t.explainHTML(w, true);
      if (/undefined|NaN/.test(st + ex)) bad.push(w.w + ':undef');
      if (ex.includes('한자·부수 풀이') || ex.includes('s-kp')) bad.push(w.w + ':kp still there');
      if (st && !ex.includes(st)) bad.push(w.w + ':story not in card');
      const ks = [...new Set(w.kj || [])].filter(c => KJ[c]);
      const m = (st.match(/class="lk"/g) || []).length; rows += m;
      if (m !== ks.length) bad.push(w.w + ':rows ' + m + '/' + ks.length);
      if (ks.length && !st.includes('<span class="sl">한자</span>')) bad.push(w.w + ':label');
      if (!ks.length && st && !st.includes('<span class="sl">이야기</span>')) bad.push(w.w + ':label(kana)');
      if (ks.length && st.includes('<span class="sl">이야기</span>')) bad.push(w.w + ':old label');
      const krm = {}; (w.kr || []).forEach(p => { (krm[p[0]] = krm[p[0]] || []).push(p[1]); });
      for (const c of ks) {
        const k = KJ[c], h = k.h.replace(/^\?\s*/, '');
        if (!st.includes('<button class="lk-big" data-act="kz" data-c="' + c + '"')) bad.push(w.w + ':btn ' + c);
        if (!st.includes('<b>' + h + '</b>')) bad.push(w.w + ':hun ' + c);
        if (KC[c]) {
          cardRows++;
          if (!st.includes('<p class="lk-x lk-hook">' + kzMark(KC[c].hook) + '</p>')) bad.push(w.w + ':hook ' + c);
          if (krm[c] && !st.includes('<small class="lk-r" lang="ja">' + [...new Set(krm[c])].join('・') + '</small>')) bad.push(w.w + ':reading ' + c);
          if (KATA.test(krm[c] ? krm[c].join('') : '')) bad.push(w.w + ':kata reading');
        } else {
          oldRows++;
          if (k.x && !st.includes('class="lk-x"')) bad.push(w.w + ':old row ' + c);
        }
      }
    }
    return { bad, rows, cardRows, oldRows, kc: Object.keys(KC).length };
  });
  ok(wr.bad.length === 0 && wr.cardRows > 0, 'every word card (' + data.words.length + ', ' + wr.rows + ' kanji rows = ' + wr.cardRows + ' with card + ' + wr.oldRows + ' old): 한자 label, 훈음 + reading / hook, no 한자·부수 풀이: ' + wr.bad.slice(0, 8).join(' | '));
  // 설정: '한자 풀이 접어 두기/펼쳐 두기' 없음
  await vis(page, '[data-act="settings"]').click(); await page.waitForTimeout(200);
  ok(await page.locator('#sheet [data-act="setKp"]').count() === 0 && !(await page.textContent('#sheet-body')).includes('한자 풀이'), 'settings: kanji-fold option removed');
  await vis(page, '#sheet .sheet-head [data-act="closeSheet"]').click(); await page.waitForTimeout(150);
  // 화면에서 한 번: 단어 카드(確認) 열어 보기
  const wid = data.words.find(w => w.w === '確認').id;
  await page.evaluate(id => { document.body.insertAdjacentHTML('beforeend', '<button id="tmp-open" data-act="open" data-id="' + id + '">x</button>'); document.getElementById('tmp-open').click(); document.getElementById('tmp-open').remove(); }, wid);
  await page.waitForSelector('#sheet:not([hidden]) .s-story', { timeout: 5000 });
  const sh = await page.evaluate(() => { const t = window.__t; const rows = [...document.querySelectorAll('#sheet-body .s-story .lk')].map(r => ({ c: r.querySelector('.lk-big').textContent, txt: r.textContent }));
    return { label: document.querySelector('#sheet-body .s-story .sl').textContent, rows, kp: document.querySelectorAll('#sheet-body .s-kp, #sheet-body .kp').length, kc: ['確', '認'].map(c => !!t.KC[c]), hooks: ['確', '認'].map(c => t.KC[c] ? t.KC[c].hook.replace(/\*\*/g, '') : '') }; });
  const rowOk = (i, hun, rd) => sh.rows[i] && sh.rows[i].txt.includes(hun) && (sh.kc[i] ? sh.rows[i].txt.includes(sh.hooks[i]) && sh.rows[i].txt.includes(rd) : true);
  ok(sh.label === '한자' && sh.rows.length === 2 && rowOk(0, '확실할 확', 'かく') && rowOk(1, '알 인', 'にん') && sh.kp === 0, '確認 card: 한자 칸 = 훈음 + reading + hook (cards: ' + sh.kc.join(',') + '), no 한자·부수 풀이: ' + sh.rows.map(r => r.txt.slice(0, 40)).join(' / '));
  await page.locator('#sheet-body .s-story .lk-big').first().click(); await page.waitForTimeout(300);
  const rd = await page.evaluate(() => [...document.querySelectorAll('#sheet-body .kz-card .kz-rd')].map(e => e.textContent).join(' '));
  ok((await page.textContent('#sheet-title')).includes('確') && rd.includes('かく') && !KATA.test(rd), '確 kanji card: 음독/훈독 in hiragana: ' + rd);
  await page.screenshot({ path: '/home/claude/work/app/shot_card_1016.png' });
  ok(errs.length === 0, 'no console errors (home folds / word card): ' + errs.join(' | '));
  await ctx.close();
}
// ---------- 9. 10/15 편의성: 소리 미리 받기·되감기·누름 표시, 아래 버튼 자리 고정, 화면 출렁임 막기, 홈 스크롤 기억 ----------
{
  const ctx9 = await browser.newContext({ viewport: { width: 1180, height: 820 }, serviceWorkers: 'block', hasTouch: true });
  await ctx9.addInitScript(() => { try { localStorage.setItem('bjt500.kzunit', '1'); } catch (e) {} });
  const page = await ctx9.newPage(); const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource|fonts\.g/.test(m.text())) errs.push(m.text()); });
  await page.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
  await page.goto(BASE);
  await page.waitForSelector('#v-home details.gf', { state: 'attached' });
  ok(await page.evaluate(() => getComputedStyle(document.body).position) !== 'fixed', 'layout unchanged (body not fixed)');
  await openFolds(page);
  await vis(page, '#v-home .book[data-i="0"]').click(); await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(900);
  const pre = await page.evaluate(() => { const t = __t, r = t.getRun(), id = t.ui.id, nx = r.ord[r.pos + 1]; const has = u => { const e = t.AMEM.m.get(u); return !!(e && e.u); }; return { cur: has(t.AUD.url('w', id)), nxt: has(t.AUD.url('w', nx)), n: t.AMEM.m.size }; });
  ok(pre.cur && pre.nxt, 'current and NEXT card word audio are already in memory: ' + JSON.stringify(pre));
  const okR1 = await page.locator('#v-study [data-act="ok"]').boundingBox();
  await page.evaluate(() => { window.__ls = 0; const a = __t.AUD.get(); a.addEventListener('loadstart', () => { window.__ls++; }); });
  await vis(page, '#v-study .cf-word').click(); await page.waitForTimeout(60);
  const t1 = await page.evaluate(() => ({ src: __t.AUD.el.src, on: document.querySelectorAll('.say-on').length, ls: window.__ls }));
  ok(t1.src.startsWith('blob:') && t1.on === 0, 'tap word: plays from memory, no visual effect: ' + t1.src.slice(0, 12));
  await page.waitForTimeout(1600);
  await vis(page, '#v-study .cf-word').click(); await page.waitForTimeout(120);
  const t2 = await page.evaluate(() => ({ src: __t.AUD.el.src, ls: window.__ls, paused: __t.AUD.el.paused }));
  ok(t2.src === t1.src && t2.ls === t1.ls && !t2.paused, 'tap again: rewinds and plays without reloading (' + t1.ls + '→' + t2.ls + ')');
  await vis(page, '[data-act="explain"]').click(); await page.waitForTimeout(380);
  const okR2 = await page.locator('#v-study [data-act="ok"]').boundingBox(), ngR2 = await page.locator('#v-study [data-act="ng"]').boundingBox();
  ok(Math.abs(okR1.x - okR2.x) < 1 && Math.abs(okR1.width - okR2.width) < 1 && Math.abs(okR1.y - okR2.y) < 1, '알고있음 stays in the same place after 해설: ' + [okR1.x, okR2.x].join('→'));
  ok(await page.locator('#v-study .ab-say').count() === 1, 'explain bar: [발음][모르겠음][알고있음]');
  await vis(page, '#v-study .ans-hw[data-act="sayW"]').click(); await page.waitForTimeout(80);
  ok(await page.evaluate(() => __t.AUD.el.src.startsWith('blob:')), 'tap the big headword in 해설 → plays');
  const sentsIn = await page.evaluate(() => { const t = __t, w = t.ui.id; return [0, 1, 2].map(i => { const e = t.AMEM.m.get(t.AUD.url('s', w, i)); return e ? (e.u ? 1 : 0) : -1; }); });
  ok(sentsIn.filter(x => x === 1).length >= 2, 'explain: sentence audio prefetched: ' + sentsIn.join(','));
  // 손가락이 조금 움직이는 진짜 탭(터치 시작→조금 이동→끝)도 버튼이 눌리는지
  {
    const cdp = await ctx9.newCDPSession(page);
    const jt = async sel => { const b = await page.locator(sel).boundingBox(); const x = b.x + b.width / 2, y = b.y + b.height / 2;
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] });
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: x + 2, y: y + 3 }] });
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] }); await page.waitForTimeout(450); };
    const nt = await page.evaluate(() => window.__ntm = (window.__ntm || 0));
    await page.evaluate(() => { window.__ntm = 0; document.addEventListener('touchmove', e => { if (e.defaultPrevented) window.__ntm++; }); });
    ok(true, 'jitter-tap helper ready');
    const p0 = await page.evaluate(() => __t.ui.mode);
    await jt('#v-study .ab-say'); await page.waitForTimeout(100);
    ok(await page.evaluate(() => __t.AUD.el.src.startsWith('blob:')), 'jitter tap on 발음 works');
    const before = await page.evaluate(() => __t.getRun().pos);
    await jt('#v-study [data-act="ok"]');
    ok(await page.evaluate(() => __t.getRun().pos) === before + 1 && await page.evaluate(() => window.__ntm) === 0, 'jitter tap on 알고있음 works, no touch is cancelled by the app');
    await jt('#v-study [data-act="explain"]');
    ok(await page.evaluate(() => __t.ui.mode) === 'explain', 'jitter tap on 해설 works');
  }
  await vis(page, '#v-study [data-act="ng"]').click(); await page.waitForTimeout(380);   // 해설 보고 모르겠음 → 다음 카드
  ok(await page.locator('#v-study .cf-word').count() === 1, 'next card after 모르겠음 in 해설');
  await vis(page, '#v-study [data-act="ng"]').click(); await page.waitForTimeout(380);   // 앞면에서 모르겠음 → 정답 공개(다음 버튼)
  const nx = await page.locator('#v-study [data-act="next"]').boundingBox(), ok3 = okR1;
  ok(Math.abs((nx.x + nx.width) - (ok3.x + ok3.width)) < 1 && nx.width > ok3.width * 1.8, '다음 → sits where 알고있음 was (right side, wide)');
  // 소리 모드: 알고있음 → 다음 카드 소리가 메모리에서 바로
  await vis(page, '#v-study [data-act="next"]').click(); await page.waitForTimeout(500);
  await vis(page, '#v-study [data-act="lis"]').click(); await page.waitForTimeout(900);
  const lt = await page.evaluate(() => new Promise(res => { const a = __t.AUD.get(); const t0 = performance.now(); let done = false;
    const on = () => { if (done) return; done = true; res({ ms: Math.round(performance.now() - t0), src: a.src.slice(0, 5) }); };
    a.addEventListener('playing', on, { once: true }); setTimeout(() => on(), 3000);
    document.querySelector('#v-study [data-act="ok"]').click(); }));
  ok(lt.src === 'blob:' && lt.ms < 1500, 'listening mode: next card plays from memory right after 알고있음 (' + lt.ms + 'ms)');
  await vis(page, '#v-study [data-act="lis"]').click(); await page.waitForTimeout(200);
  // 홈 스크롤 기억
  await vis(page, '[data-act="exit"]').click(); await page.waitForSelector('#v-home .grp-basic');
  await page.evaluate(() => { const sc = document.querySelector('#v-home .scroll'); sc.scrollTop = 1400; sc.dispatchEvent(new Event('scroll')); });
  await page.waitForTimeout(150);
  const before = await page.evaluate(() => document.querySelector('#v-home .scroll').scrollTop);
  const bk = page.locator('#v-home .book >> visible=true');
  let clicked = false;
  for (let k = 0; k < await bk.count(); k++) { const bb = await bk.nth(k).boundingBox(); if (bb && bb.y > 120 && bb.y < 600) { await bk.nth(k).click({ position: { x: bb.width / 2, y: 30 } }); clicked = true; break; } }
  if (clicked) { await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(300); await vis(page, '[data-act="exit"]').click(); await page.waitForSelector('#v-home .grp-basic'); await page.waitForTimeout(150); }
  const after = await page.evaluate(() => document.querySelector('#v-home .scroll').scrollTop);
  ok(clicked && before > 1000 && Math.abs(after - before) < 4, 'home keeps its scroll position after a chapter: ' + before + '→' + after);
  ok(errs.length === 0, 'no console errors (usability): ' + errs.join(' | '));
  await ctx9.close();
}

/* ===================== 10/16: 한자칸 · 한자 카드 시트 · 한자 단원 ===================== */
const sortNoT = id => { const w = byId.get(id); return w.ord != null ? w.ord : 1e6 + w.bn; };
const toHiraT = s => String(s || '').replace(/[ァ-ヶ]/g, c => String.fromCharCode(c.charCodeAt(0) - 0x60));
const openWordT = (page, id) => page.evaluate(id => { document.body.insertAdjacentHTML('beforeend', '<button id="tmp-open" data-act="open" data-id="' + id + '">x</button>'); document.getElementById('tmp-open').click(); document.getElementById('tmp-open').remove(); }, id);
const openKzT = (page, c) => page.evaluate(c => { document.body.insertAdjacentHTML('beforeend', '<button id="tmp-kz" data-act="kz" data-c="' + c + '">x</button>'); document.getElementById('tmp-kz').click(); document.getElementById('tmp-kz').remove(); }, c);
const overT = (page, sel) => page.evaluate(sel => { const el = document.querySelector(sel); return Math.max(document.documentElement.scrollWidth - innerWidth, el ? el.scrollWidth - el.clientWidth : 999); }, sel);
const KZSRC = JSON.parse(fs.readFileSync('/home/claude/work/kanji_mn/kanji_src.json', 'utf8')).map(k => k.c);

// ---------- 10. 네모 한자 → 한자 카드 시트(단어 카드 시트와 같은 쌓기·뒤로가기) · 같은 한자 칸 네모 한자도 ----------
{
  const probe = await newPage({ width: 1180, height: 820 });
  await probe.page.waitForSelector('#v-home details.gf', { state: 'attached' });
  const KCK = new Set(await probe.page.evaluate(() => Object.keys(__t.KC)));
  await probe.ctx.close();
  const relOf = (c, w) => [...new Set(data.kanji[c].u)].filter(i => i !== w.id && byId.has(i));
  const mains = data.words.filter(w => w.ord != null).sort((a, b) => a.ord - b.ord);
  const pick = f => mains.find(w => w.kj.some(c => data.kanji[c] && f(c) && relOf(c, w).length >= 2));
  const w0 = pick(c => KCK.has(c)) || pick(() => true);
  const c0 = w0.kj.find(c => data.kanji[c] && KCK.has(c) && relOf(c, w0).length >= 2) || w0.kj.find(c => data.kanji[c] && relOf(c, w0).length >= 2);
  const { ctx, page, errs } = await newPage({ width: 1180, height: 820 }, seed(H0({ [w0.id]: { n: 1, m: 6, l: 0, t: 1, pin: 0, rm: -1, u: 1 } })));
  await page.waitForSelector('#v-home .wk-top');
  const title = () => page.textContent('#sheet-title');
  // 시트 안: 단어 카드 → 한자칸 한자 → 한자 카드 → 단어 → 뒤로 → 한자 카드 → 뒤로 → 원래 단어
  await openWordT(page, w0.id); await page.waitForSelector('#sheet:not([hidden]) .s-story');
  ok((await title()).includes(w0.w) && await page.locator('#sheet-back').isHidden() && (await page.textContent('#sheet-body .s-story .sl')) === '한자', 'word card sheet ' + w0.w + ': 한자 칸');
  await page.locator('#sheet-body .s-story .lk-big[data-c="' + c0 + '"]').click(); await page.waitForTimeout(300);
  ok((await title()).includes(c0) && await page.locator('#sheet-body .kz-card').count() === 1 && await page.locator('#sheet-back').isVisible(), '한자칸 ' + c0 + ' → kanji card sheet, stacked (back shown)');
  if (KCK.has(c0)) ok((await page.textContent('#sheet-body .kz-hook')).length > 5 && await page.locator('#sheet-body .kz-strip .kz-pn').count() === 3 && await page.locator('#sheet-body .kz-tree').count() === 1, 'kanji card: scene line + 3 pictures + 부수로 쪼개 보기');
  const exp = [...new Set(data.kanji[c0].u)].filter(i => byId.has(i)).sort((a, b) => sortNoT(a) - sortNoT(b));
  const got = await page.$$eval('#sheet-body .kzu-ws .sk-w', els => els.map(e => +e.dataset.id));
  ok(got.length === exp.length && got.join() === exp.join(), 'word list at the bottom: all ' + exp.length + ' words with ' + c0 + ' (main order → basic order)');
  ok(await page.locator('#sheet-body .kzu-ws .sk-w .sk-j rt').count() > 0 && await page.locator('#sheet-body .kzu-ws .sk-w .sk-m').count() === exp.length && await page.locator('#sheet-body .kzu-ws .sk-w[data-act="open"]').count() === exp.length, 'word list: big word + reading + short meaning, each opens the word');
  const w1 = byId.get(got.find(i => i !== w0.id));
  await page.locator('#sheet-body .kzu-ws .sk-w[data-id="' + w1.id + '"]').click(); await page.waitForTimeout(300);
  ok((await title()).includes(w1.w) && await page.locator('#sheet-body .s-ans').count() === 1 && await page.locator('#sheet-back').isVisible(), 'tap a word → its word card: ' + w1.w);
  await page.locator('#sheet-back').click(); await page.waitForTimeout(300);
  ok((await title()).includes(c0) && await page.locator('#sheet-body .kz-card').count() === 1 && await page.locator('#sheet-back').isVisible(), 'back → kanji card');
  await page.locator('#sheet-back').click(); await page.waitForTimeout(300);
  ok((await title()).includes(w0.w) && await page.locator('#sheet-body .s-ans').count() === 1 && await page.locator('#sheet-back').isHidden(), 'back → the original word card');
  const skIn = page.locator('#sheet-body .sk .sk-k').first();
  const cs = await skIn.textContent();
  await skIn.click(); await page.waitForTimeout(300);
  ok((await title()).includes(cs) && await page.locator('#sheet-body .kz-card').count() === 1 && await page.locator('#sheet-back').isVisible(), '같은 한자 칸 네모 한자 ' + cs + ' (in sheet) → kanji card, stacked');
  await vis(page, '#sheet .sheet-head [data-act="closeSheet"]').click(); await page.waitForTimeout(200);
  ok(await page.evaluate(() => __t.sheetStack.length) === 0, 'closing the sheet clears the stack');
  // 시트 밖(해설 화면)에서 누르면 새로 시작
  await vis(page, '#v-home .wk-top [data-act="weakNew"]').click(); await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(350);
  await vis(page, '[data-act="explain"]').click(); await page.waitForTimeout(400);
  const sk = page.locator('#v-study .sk .sk-k').first(), c2 = await sk.textContent();
  await sk.click(); await page.waitForTimeout(300);
  ok((await title()).includes(c2) && await page.locator('#sheet-body .kz-card').count() === 1 && await page.locator('#sheet-back').isHidden(), 'explain screen: 같은 한자 칸 ' + c2 + ' → kanji card (new stack)');
  await vis(page, '#sheet .sheet-head [data-act="closeSheet"]').click(); await page.waitForTimeout(200);
  await page.locator('#v-study .s-story .lk-big[data-c="' + c0 + '"]').click(); await page.waitForTimeout(300);
  ok((await title()).includes(c0) && await page.locator('#sheet-back').isHidden(), 'explain screen: 한자칸 ' + c0 + ' → kanji card (new stack)');
  await page.locator('#sheet-body .kzu-ws .sk-w[data-id="' + w1.id + '"]').click(); await page.waitForTimeout(300);
  ok((await title()).includes(w1.w) && await page.locator('#sheet-back').isVisible(), '→ word card, back shown');
  await page.locator('#sheet-back').click(); await page.waitForTimeout(300);
  ok((await title()).includes(c0) && await page.locator('#sheet-back').isHidden(), 'back → kanji card (stack bottom)');
  await vis(page, '#sheet .sheet-head [data-act="closeSheet"]').click(); await page.waitForTimeout(200);
  ok(await page.evaluate(() => __t.ui.mode) === 'explain' && await page.locator('#v-study .ex').count() === 1 && await page.locator('#v-study .s-kp').count() === 0, 'sheet closed → same explain screen (no 한자·부수 풀이)');
  await page.screenshot({ path: '/home/claude/work/app/shot_explain_1016.png' });
  ok(errs.length === 0, 'no console errors (kanji card sheet): ' + errs.join(' | '));
  await ctx.close();
}

// ---------- 11. 한자 단원: 홈 묶음 → 첫 장 → 앞면 한자만 → 해설 카드 → 모르겠음/알고있음 → 장 끝 → 기록 저장(새로고침 후) → 단어 기록·약점 그대로 ----------
{
  const wkId = ORDER[3];
  const { ctx, page, errs } = await newPage({ width: 1180, height: 820 }, seed(H0({ [wkId]: { n: 2, m: 6, l: 0, t: 1, pin: 0, rm: -1, u: 1 }, [ORDER[4]]: { n: 1, m: 1, l: 1, t: 1, pin: 0, rm: -1, u: 1 } })));
  await page.waitForSelector('#v-home details[data-g="kz"]', { state: 'attached' });
  const Hbefore = await page.evaluate(() => localStorage.getItem('bjt500.hoedok.v2'));
  ok(await page.evaluate(() => localStorage.getItem('bjt500.kanji.v1')) === null, 'no kanji record before the kanji unit is used');
  const homeTxt = async () => ({ wk: (await page.textContent('#v-home .wk-top b')).trim(), stats: (await page.textContent('#v-home .stats')).trim(), banner: (await page.textContent('#v-home .resume')).trim() });
  const t0 = await homeTxt();
  const layout = await page.evaluate(() => [...document.querySelector('#v-home .home').children].map(e => { const d = e.querySelector(':scope > details.gf'); return d ? 'fold:' + d.dataset.g : e.querySelector('.zrow') ? 'zrow' : e.className; }));
  const iz = layout.indexOf('fold:kz');
  ok(iz > layout.indexOf('fold:p2') && layout.indexOf('fold:p2') > 0 && iz < layout.indexOf('zrow'), 'kanji fold after 1–3부, above the word-list row: ' + layout.join(','));
  const kz = await page.evaluate(() => ({ o: __t.KZO, ch: __t.KZCH.map(c => [c.a, c.b, c.kind, c.ids.join('')]) }));
  const gc = genChapters(950);
  ok(kz.o.join('') === KZSRC.join('') && kz.ch.length === gc.length && kz.ch.every((c, i) => c[0] === gc[i].a && c[1] === gc[i].b && c[2] === gc[i].kind && c[3] === KZSRC.slice(c[0] - 1, c[1]).join('')), 'kanji chapters = word rule on 950 kanji (most used first): ' + kz.ch.length + ' chapters');
  const sum = (await page.textContent('#v-home details[data-g="kz"] > summary')).trim();
  ok(sum.startsWith('한자') && sum.includes('1–950자') && sum.includes('끝낸 장 0/' + gc.length), 'kanji fold header: ' + sum);
  await page.locator('#v-home details[data-g="kz"] > summary').click(); await page.waitForTimeout(150);
  ok(await page.locator('#v-home details[data-g="kz"] .book >> visible=true').count() === gc.length, 'tap opens the kanji fold (' + gc.length + ' chapters)');
  await vis(page, '#v-home .kzu-book[data-k="0"]').click(); await page.waitForSelector('#v-kz .cf-word'); await page.waitForTimeout(350);
  const run0 = await page.evaluate(() => __t.kzRun());
  ok(run0.ord.length === 50 && [...run0.ord].sort().join('') === KZSRC.slice(0, 50).sort().join(''), '漢字1章 = 50 most used kanji (shuffled)');
  const fr = await page.evaluate(() => ({ word: document.querySelector('#v-kz .cf-word').textContent, stage: document.querySelector('#v-kz .stage').textContent, card: document.querySelectorAll('#v-kz .kz-card').length,
    acts: [...document.querySelectorAll('#v-kz .abar [data-act]')].map(b => b.dataset.act).join(','), noise: document.querySelectorAll('#v-kz [data-act="sayW"], #v-kz [data-act="star"], #v-kz [data-act="lis"], #v-kz .spk').length,
    ff: getComputedStyle(document.querySelector('#v-kz .cf-word')).fontFamily, kyo: (() => { const d = document.createElement('div'); d.style.fontFamily = 'var(--f-kyo)'; document.body.appendChild(d); const f = getComputedStyle(d).fontFamily; d.remove(); return f; })(),
    title: document.querySelector('#v-kz .sb-t').textContent, study: !document.getElementById('v-study').hidden }));
  const k0 = run0.ord[0], kd = data.kanji[k0];
  ok(fr.word === k0 && fr.card === 0 && !fr.stage.includes(kd.h.replace(/^\?\s*/, '')) && !kd.on.concat(kd.kun).some(o => fr.stage.includes(toHiraT(o).replace(/[()]/g, ''))), 'front: only the kanji ' + k0 + ' (no meaning, readings or card)');
  ok(fr.acts === 'kzExplain,kzNg,kzOk' && fr.noise === 0 && fr.ff === fr.kyo && !fr.study, 'front bar [해설][모르겠음][알고있음], no sound/star buttons, 단어장 font (--f-kyo)');
  ok(fr.title.includes('漢字1章') && fr.title.includes('1회독') && fr.title.includes('1–50자'), 'study bar: ' + fr.title);
  const okR1 = await page.locator('#v-kz [data-act="kzOk"]').boundingBox();
  await vis(page, '#v-kz [data-act="kzExplain"]').click(); await page.waitForTimeout(380);
  const rv = await page.evaluate(() => ({ card: document.querySelectorAll('#v-kz .kz-card').length, words: document.querySelectorAll('#v-kz .kzu-ws .sk-w').length, acts: [...document.querySelectorAll('#v-kz .abar-in > *')].map(b => b.dataset.act || b.className).join(','), html: document.getElementById('v-kz').innerHTML }));
  ok(rv.card === 1 && rv.words === [...new Set(kd.u)].filter(i => byId.has(i)).length && !/undefined|NaN/.test(rv.html), '해설 = kanji card with its ' + rv.words + ' words');
  ok(rv.acts === 'kzSay,kzNg,kzOk', 'explain bar: [발음][모르겠음][알고있음] (10/20 한자 소리)');
  const okR2 = await page.locator('#v-kz [data-act="kzOk"]').boundingBox();
  ok(Math.abs(okR1.x - okR2.x) < 1 && Math.abs(okR1.width - okR2.width) < 1 && Math.abs(okR1.y - okR2.y) < 1, '알고있음 stays in the same place after 해설');
  await page.screenshot({ path: '/home/claude/work/app/shot_kz_explain_1180.png' });
  const wid = +(await page.locator('#v-kz .kzu-ws .sk-w').first().getAttribute('data-id'));
  await page.locator('#v-kz .kzu-ws .sk-w').first().click(); await page.waitForTimeout(300);
  ok((await page.textContent('#sheet-title')).includes(byId.get(wid).w) && await page.locator('#sheet-body .s-ans').count() === 1, 'tap a word in the kanji card → word card sheet');
  await vis(page, '#sheet .sheet-head [data-act="closeSheet"]').click(); await page.waitForTimeout(200);
  await vis(page, '#v-kz [data-act="kzNg"]').click(); await page.waitForTimeout(380);   // 해설 보고 모르겠음 → 다음 한자
  ok(await page.locator('#v-kz .cf-word').count() === 1 && await page.evaluate(() => __t.kzRun().pos) === 1, '모르겠음 after 해설 → next kanji');
  const k1 = await page.evaluate(() => __t.kui.c);
  await vis(page, '#v-kz [data-act="kzNg"]').click(); await page.waitForTimeout(380);   // 앞면에서 모르겠음 → 카드 + 다음
  const un = await page.evaluate(() => ({ mode: __t.kui.mode, card: document.querySelectorAll('#v-kz .kz-card').length, acts: [...document.querySelectorAll('#v-kz .abar-in > *')].map(b => b.dataset.act || b.className).join(',') }));
  ok(un.mode === 'unknown' && un.card === 1 && un.acts === 'kzSay,kzNext', '모르겠음 on the front → card shown + [발음][다음 →]');
  const nxb = await page.locator('#v-kz [data-act="kzNext"]').boundingBox();
  ok(Math.abs((nxb.x + nxb.width) - (okR1.x + okR1.width)) < 1 && nxb.width > okR1.width * 1.8, '다음 → sits where 알고있음 was');
  await vis(page, '#v-kz [data-act="kzNext"]').click(); await page.waitForTimeout(380);
  await vis(page, '#v-kz [data-act="kzOk"]').click(); await page.waitForTimeout(380);
  await vis(page, '#v-kz [data-act="kzUndo"]').click(); await page.waitForTimeout(300);
  ok(await page.evaluate(() => __t.kzRun().pos) === 2 && (await page.textContent('#toast')).includes('되돌렸어요'), 'undo (이전) returns to the previous kanji');
  for (let i = 0; i < 60; i++) {
    if (await page.locator('#modal:not([hidden])').count()) break;
    await vis(page, '#v-kz [data-act="kzOk"]').click(); await page.waitForTimeout(320);
  }
  ok(await page.locator('#modal:not([hidden]) [data-act="kzLoopGo"]').count() === 2 && (await page.textContent('#modal h2')).includes('2개'), 'end of the main pass: 2 unknown kanji → shuffle question');
  await vis(page, '#modal [data-act="kzLoopGo"][data-v="0"]').click(); await page.waitForSelector('#v-kz .cf-word'); await page.waitForTimeout(350);
  const lp = await page.evaluate(() => ({ r: __t.kzRun(), c: __t.kui.c, phase: (document.querySelector('#v-kz .phase') || {}).textContent || '' }));
  ok(lp.r.ph === 'loop' && lp.r.round === 1 && lp.r.shuf === false && lp.c === k0 && lp.phase.includes('1라운드'), 'round 1 (in order) starts with the first missed kanji');
  await vis(page, '#v-kz [data-act="kzNg"]').click(); await page.waitForTimeout(380);
  await vis(page, '#v-kz [data-act="kzNext"]').click(); await page.waitForTimeout(380);
  await vis(page, '#v-kz [data-act="kzOk"]').click(); await page.waitForTimeout(380);
  ok(await page.locator('#modal:not([hidden]) [data-act="kzRoundGo"]').count() === 2 && (await page.textContent('#modal h2')).includes('1개'), 'round 2 question (1 kanji left)');
  await vis(page, '#modal [data-act="kzRoundGo"][data-v="1"]').click(); await page.waitForSelector('#v-kz .cf-word'); await page.waitForTimeout(350);
  ok((await page.textContent('#toast')).includes('2라운드') && await page.evaluate(() => __t.kzRun().shuf) === true, 'round 2 (shuffled)');
  await vis(page, '#v-kz [data-act="kzOk"]').click(); await page.waitForTimeout(400);
  ok(await page.locator('#modal:not([hidden]) .sum').count() === 1 && (await page.textContent('#modal .sum')).includes('漢字1章') && (await page.textContent('#modal .sum')).includes('48 / 50'), 'summary after the whole chapter (48/50)');
  const key0 = await page.evaluate(() => __t.KZCH[0].key);
  const kr = await page.evaluate(() => JSON.parse(localStorage.getItem('bjt500.kanji.v1')));
  ok(kr && kr.ch[key0] && kr.ch[key0].n === 1 && kr.ch[key0].cur === null && kr.ch[key0].last.k === 48 && kr.ch[key0].last.r === 2, 'kanji record (bjt500.kanji.v1): 漢字1章 done once, 48/50, 2 rounds');
  ok(Object.keys(kr.w).length === 50 && kr.w[k0].m === 2 && kr.w[k1].m === 1 && Object.values(kr.w).every(x => x.n === 1), 'per-kanji records: 50 kanji, misses ' + k0 + '×2 ' + k1 + '×1');
  ok(await page.locator('#modal [data-act="kzOpen"][data-k="1"]').count() === 1 && (await page.textContent('#modal [data-act="kzOpen"][data-k="1"]')).includes('漢字2章') && await page.locator('#modal [data-act="kzOpen"][data-k="0"]').count() === 1, 'summary offers 漢字2章 시작 / 이 장 한 번 더');
  ok(await page.evaluate(() => localStorage.getItem('bjt500.hoedok.v2')) === Hbefore, 'word records (bjt500.hoedok.v2) untouched by the kanji unit');
  await vis(page, '#modal [data-act="home"]').click(); await page.waitForSelector('#v-home details[data-g="kz"]', { state: 'attached' });
  const t1 = await homeTxt();
  ok(t1.wk === t0.wk && t1.stats === t0.stats && t1.banner === t0.banner && !t1.banner.includes('漢字'), 'home: weak count, word stats, next-chapter banner unchanged (' + t1.wk + ' | ' + t1.stats + ')');
  ok((await page.textContent('#v-home details[data-g="kz"] > summary')).includes('끝낸 장 1/' + gc.length), 'kanji fold: 끝낸 장 1/' + gc.length);
  await page.reload(); await page.waitForSelector('#v-home details[data-g="kz"]', { state: 'attached' });
  ok((await page.textContent('#v-home details[data-g="kz"] > summary')).includes('끝낸 장 1/' + gc.length) && await page.evaluate(() => localStorage.getItem('bjt500.hoedok.v2')) === Hbefore, 'after reload: kanji record kept, word records identical');
  await page.evaluate(() => { document.querySelector('#v-home details[data-g="kz"]').open = true; });
  const b0 = await page.textContent('#v-home .kzu-book[data-k="0"]');
  ok(b0.includes('2회독') && b0.includes('1회 완료') && b0.includes('96% 알고있음'), 'after reload: 漢字1章 book shows 2회독 · 1회 완료 · 96%');
  ok(await page.evaluate(id => __t.isWeak(id), wkId) === true && await page.evaluate(() => Object.keys(__t.H.ch).length) === 0 && (await page.textContent('#v-home .wk-top b')).trim() === t0.wk, 'after reload: weak words and word chapter records unchanged');
  // 이어서 하기: 漢字2章 세 개 하고 닫기 → 새로고침 → 그 자리에서 이어서 · 키보드
  await vis(page, '#v-home .kzu-book[data-k="1"]').click(); await page.waitForSelector('#v-kz .cf-word'); await page.waitForTimeout(350);
  for (let i = 0; i < 3; i++) { await vis(page, '#v-kz [data-act="kzOk"]').click(); await page.waitForTimeout(330); }
  await vis(page, '#v-kz [data-act="kzExit"]').click(); await page.waitForSelector('#v-home details[data-g="kz"]', { state: 'attached' });
  ok((await page.textContent('#v-home details[data-g="kz"] > summary')).includes('진행중'), 'kanji fold shows 진행중 after closing mid-chapter');
  await page.reload(); await page.waitForSelector('#v-home details[data-g="kz"]', { state: 'attached' });
  await page.evaluate(() => { document.querySelector('#v-home details[data-g="kz"]').open = true; });
  ok((await page.textContent('#v-home .kzu-book[data-k="1"]')).includes('진행 4/100'), 'book shows 진행 4/100 after reload');
  await vis(page, '#v-home .kzu-book[data-k="1"]').click(); await page.waitForSelector('#v-kz .cf-word'); await page.waitForTimeout(400);
  ok(await page.evaluate(() => __t.kzRun().pos) === 3 && (await page.textContent('#toast')).includes('이어서'), 'resumes 漢字2章 at 4/100');
  await page.keyboard.press('Space'); await page.waitForTimeout(380);
  ok(await page.evaluate(() => __t.kui.mode) === 'explain', 'keyboard: space → 해설');
  await page.keyboard.press('2'); await page.waitForTimeout(380);
  ok(await page.evaluate(() => __t.kzRun().pos) === 4 && await page.evaluate(() => __t.kui.mode) === 'front', 'keyboard: 2 → 알고있음');
  await page.keyboard.press('Escape'); await page.waitForTimeout(300);
  ok(await page.locator('#v-home details[data-g="kz"]').count() === 1 && await page.evaluate(() => document.getElementById('v-kz').hidden), 'Esc → home');
  ok(await page.evaluate(() => localStorage.getItem('bjt500.hoedok.v2')) === Hbefore, 'word records still identical after more kanji study');
  // ↺ 처음부터: 진행 중인 漢字2章을 처음부터
  await page.evaluate(() => { document.querySelector('#v-home details[data-g="kz"]').open = true; });
  await vis(page, '#v-home .kzu-book[data-k="1"] [data-act="kzRestart"]').click(); await vis(page, '#modal [data-act="cfmOk"]').click(); await page.waitForSelector('#v-kz .cf-word'); await page.waitForTimeout(350);
  ok(await page.evaluate(() => __t.kzRun().pos === 0 && __t.kzRun().ord.length === 100), '↺ restart: 漢字2章 starts again from 1/100');
  await vis(page, '#v-kz [data-act="kzExit"]').click(); await page.waitForSelector('#v-home details[data-g="kz"]', { state: 'attached' });
  // 한자 장 목록(시트): 줄 → 한자 카드(쌓기) → 뒤로 → 목록 · 이 장 기록 초기화
  await page.evaluate(() => { document.querySelector('#v-home details[data-g="kz"]').open = true; });
  await vis(page, '#v-home .kzu-book[data-k="1"] [data-act="kzList"]').click(); await page.waitForTimeout(300);
  ok(await page.locator('#sheet-body #kz-list > li').count() === 100 && (await page.textContent('#sheet-title')).includes('漢字2章'), 'kanji chapter list sheet: 100 kanji');
  const lc = await page.locator('#sheet-body #kz-list .row').first().getAttribute('data-c');
  await page.locator('#sheet-body #kz-list .row').first().click(); await page.waitForTimeout(300);
  ok((await page.textContent('#sheet-title')).includes(lc) && await page.locator('#sheet-body .kz-card').count() === 1 && await page.locator('#sheet-back').isVisible(), 'list row → kanji card (stacked)');
  await page.locator('#sheet-back').click(); await page.waitForTimeout(300);
  ok(await page.locator('#sheet-body #kz-list > li').count() === 100, 'back → chapter list');
  await vis(page, '#sheet-body [data-act="kzReset"]').click(); await vis(page, '#modal [data-act="cfmOk"]').click(); await page.waitForTimeout(300);
  await page.evaluate(() => { document.querySelector('#v-home details[data-g="kz"]').open = true; });
  const b1 = await page.textContent('#v-home .kzu-book[data-k="1"]');
  ok(!b1.includes('진행') && b1.includes('1회독') && await page.evaluate(() => __t.KZ.ch[__t.KZCH[1].key].cur === null && Object.keys(__t.KZ.w).length >= 50), 'chapter reset clears that chapter only (per-kanji records kept)');
  ok(await page.evaluate(() => localStorage.getItem('bjt500.hoedok.v2')) === Hbefore, 'word records still identical after the kanji chapter reset');
  // 진도 백업: 한자 기록도 같이 내보내고 가져옴(단어 기록은 예전처럼)
  await vis(page, '[data-act="settings"]').click(); await vis(page, '[data-act="exportOpen"]').click(); await page.waitForSelector('#code-out');
  const code = await page.inputValue('#code-out');
  await vis(page, '#modal [data-act="cfmNo"]').click();
  await page.evaluate(() => localStorage.removeItem('bjt500.kanji.v1'));
  await page.reload(); await page.waitForSelector('#v-home details[data-g="kz"]', { state: 'attached' });
  ok((await page.textContent('#v-home details[data-g="kz"] > summary')).includes('끝낸 장 0/'), 'kanji record removed → 끝낸 장 0');
  await vis(page, '[data-act="settings"]').click(); await vis(page, '[data-act="importOpen"]').click();
  await page.fill('#code-in', code); await vis(page, '[data-act="importGo"]').click(); await page.waitForTimeout(500);
  ok((await page.textContent('#v-home details[data-g="kz"] > summary')).includes('끝낸 장 1/') && (await page.textContent('#toast')).includes('한자 기록'), 'import restores kanji records: ' + (await page.textContent('#toast')));
  const h3 = await page.evaluate(() => JSON.parse(localStorage.getItem('bjt500.hoedok.v2')));
  ok(h3.w[wkId] && h3.w[wkId].m === 6 && Object.keys(h3.w).length === 2 && Object.keys(h3.ch).length === 0, 'import keeps word records as they were');
  ok(errs.length === 0, 'no console errors (kanji unit): ' + errs.join(' | '));
  await ctx.close();
}

// ---------- 11b. 망가진 한자 기록·예전 설정(kp: true)이 남아 있어도 오류 없음 ----------
{
  const init = `(() => { if (sessionStorage.getItem('seeded')) return; sessionStorage.setItem('seeded','1');
    localStorage.setItem('bjt500.kanji.v1', JSON.stringify({ch: {'K:zz.50:1-50:step': {n: 'x', cur: {ord: ['A', 5, null]}}, junk: 1}, w: {'日': {n: -3, m: 'q'}, 'Z': {}}, g: 7, u: 'no'}));
    localStorage.setItem('bjt500.prefs.v2', JSON.stringify({auto: true, rate: 1, sent: true, shuf: false, wkN: 5, wv: 2, furi: 'all', tr: 'show', kp: true, exam: '2026-10-22', em: 3, u: 1})); })();`;
  const { ctx, page, errs } = await newPage({ width: 1180, height: 820 }, init);
  await page.waitForSelector('#v-home details[data-g="kz"]', { state: 'attached' });
  ok((await page.textContent('#v-home details[data-g="kz"] > summary')).includes('끝낸 장 0/') && await page.evaluate(() => JSON.stringify(__t.KZ.w['日'])) === '{"n":0,"m":0,"l":-1,"t":0,"u":0}', 'junk kanji record is cleaned (home renders, 0 done)');
  await page.evaluate(() => { document.querySelector('#v-home details[data-g="kz"]').open = true; });
  await vis(page, '#v-home .kzu-book[data-k="0"]').click(); await page.waitForSelector('#v-kz .cf-word'); await page.waitForTimeout(350);
  ok(await page.evaluate(() => __t.kzRun().ord.length) === 50, 'kanji chapter starts fine after junk record');
  await vis(page, '#v-kz [data-act="kzExit"]').click(); await page.waitForSelector('#v-home .wk-top');
  await openWordT(page, ORDER[0]); await page.waitForSelector('#sheet:not([hidden]) .s-ans');
  ok(await page.evaluate(() => __t.S.kp) === true && await page.locator('#sheet-body .s-kp, #sheet-body .kp').count() === 0, 'old setting kp: true kept but ignored (no 한자·부수 풀이)');
  ok(errs.length === 0, 'no console errors (junk kanji record / old kp setting): ' + errs.join(' | '));
  await ctx.close();
}

// ---------- 12. 단어 장 하나를 처음부터 끝까지(기존 흐름 그대로) · 한자 기록은 안 생김 ----------
{
  const { ctx, page, errs } = await newPage({ width: 1180, height: 820 });
  await page.waitForSelector('#v-home .book', { state: 'attached' }); await openFolds(page);
  await vis(page, '#v-home .book[data-i="0"]').click(); await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(350);
  const ord = await page.evaluate(() => __t.getRun().ord);
  ok(ord.length === 50 && [...ord].sort((a, b) => a - b).join() === ORDER.slice(0, 50).sort((a, b) => a - b).join(), '第1章 = No.1–50');
  const id0 = await page.evaluate(() => __t.ui.id), w0 = byId.get(id0);
  await vis(page, '[data-act="explain"]').click(); await page.waitForTimeout(380);
  const lab = await page.evaluate(() => { const e = document.querySelector('#v-study .s-story .sl'); return e ? e.textContent : ''; });
  ok(lab === ([...new Set(w0.kj)].some(c => data.kanji[c]) ? '한자' : '이야기') && await page.locator('#v-study .s-kp').count() === 0, 'explain: story label ' + lab + ', no 한자·부수 풀이');
  await vis(page, '#v-study [data-act="ng"]').click(); await page.waitForTimeout(380);
  const id1 = await page.evaluate(() => __t.ui.id);
  await vis(page, '#v-study [data-act="ng"]').click(); await page.waitForTimeout(380);
  ok(await page.evaluate(() => __t.ui.mode) === 'unknown' && await page.locator('#v-study [data-act="next"]').count() === 1, 'front 모르겠음 → answer + [다음 →]');
  await vis(page, '#v-study [data-act="next"]').click(); await page.waitForTimeout(380);
  for (let i = 0; i < 60; i++) {
    if (await page.locator('#modal:not([hidden])').count()) break;
    await vis(page, '#v-study [data-act="ok"]').click(); await page.waitForTimeout(310);
  }
  ok(await page.locator('#modal:not([hidden]) [data-act="loopGo"]').count() === 2 && (await page.textContent('#modal h2')).includes('2개'), 'main pass done: 2 unknown words → loop question');
  await vis(page, '#modal [data-act="loopGo"][data-v="1"]').click(); await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(350);
  for (let i = 0; i < 4; i++) { if (await page.locator('#modal:not([hidden])').count()) break; await vis(page, '#v-study [data-act="ok"]').click(); await page.waitForTimeout(340); }
  ok(await page.locator('#modal:not([hidden]) .sum').count() === 1 && (await page.textContent('#modal .sum')).includes('48 / 50'), 'summary: 48/50');
  const h = await page.evaluate(() => JSON.parse(localStorage.getItem('bjt500.hoedok.v2')));
  ok(h.ch[0] && h.ch[0].n === 1 && h.ch[0].cur === null && h.ch[0].last.k === 48 && h.ch[0].last.tot === 50 && h.ch[0].last.r === 1, 'word chapter record: 1회 완료, 48/50, 1 round');
  ok(Object.keys(h.w).length === 50 && Object.values(h.w).every(x => x.n === 1) && h.w[id0].m === 1 && h.w[id1].m === 1 && Object.values(h.w).filter(x => x.m).length === 2, 'word records: 50 words seen once, 2 misses kept');
  ok(await page.evaluate(() => localStorage.getItem('bjt500.kanji.v1')) === null, 'word study writes no kanji record');
  await vis(page, '#modal [data-act="home"]').click(); await page.waitForSelector('#v-home .stats');
  ok((await page.textContent('#v-home .stats')).includes('본 단어 50/') && (await page.textContent('#v-home .stats')).includes('끝낸 장 1/'), 'home stats: 50 seen, 1 chapter done');
  ok((await page.textContent('#v-home details[data-g="kz"] > summary')).includes('끝낸 장 0/'), 'kanji fold unaffected by word study');
  ok(errs.length === 0, 'no console errors (word chapter end to end): ' + errs.join(' | '));
  await ctx.close();
}

// ---------- 13. 한자 카드 전부 그리기(undefined/NaN·SVG 오류 없음) · 세 화면 크기 가로 넘침 없음(카드 표본 + 한자 단원 화면) ----------
{
  const cardsFile = fs.existsSync('/home/claude/work/kz/kz_cards.json') ? JSON.parse(fs.readFileSync('/home/claude/work/kz/kz_cards.json', 'utf8')) : [];
  const { ctx, page, errs } = await newPage({ width: 1180, height: 820 });
  await page.waitForSelector('#v-home details.gf', { state: 'attached' });
  const all = await page.evaluate(() => {
    const t = __t, bad = []; let n = 0, full = 0;
    for (const c of t.KZO) {
      const h = t.kzBodyHTML(c); n++;
      if (typeof h !== 'string' || /undefined|NaN|\[object /.test(h)) bad.push(c);
      if (t.KC[c]) { if (h.includes('kz-simple') || !h.includes('class="kz-hook"') || !h.includes('kz-strip')) bad.push(c + ':fallback'); else full++; }
      else if (!h.includes('kz-simple')) bad.push(c + ':shape');
    }
    return { n, full, kc: Object.keys(t.KC).length, bad };
  });
  ok(all.bad.length === 0 && all.n === 950 && all.full === all.kc && all.kc === new Set(cardsFile.map(c => c.c)).size, 'all ' + all.n + ' kanji render: ' + all.full + ' full cards (= kz_cards.json ' + cardsFile.length + ') + ' + (all.n - all.full) + ' simple, no undefined/NaN: ' + all.bad.slice(0, 10).join(' '));
  // 실제 화면에 전부 붙여서 그려 보기(SVG 경로 오류 등은 콘솔 오류로 잡힘)
  const drawn = await page.evaluate(async () => {
    const t = __t, box = document.createElement('div'); box.style.cssText = 'position:absolute;left:0;top:0;width:900px;visibility:hidden'; document.body.appendChild(box);
    let svgs = 0;
    for (let i = 0; i < t.KZO.length; i += 50) { box.innerHTML = t.KZO.slice(i, i + 50).map(c => t.kzBodyHTML(c)).join(''); svgs += box.querySelectorAll('svg').length; await new Promise(r => requestAnimationFrame(r)); }
    box.remove(); return svgs;
  });
  ok(drawn > 0 && errs.length === 0, 'all 950 kanji cards drawn in the page (' + drawn + ' svg), no console errors: ' + errs.slice(0, 3).join(' | '));
  // 카드가 없는 한자(자료가 덜 찼을 때) · 그리는 스크립트가 없을 때도 오류 없이 간단한 카드/옛 줄로
  const fb = await page.evaluate(() => {
    const t = __t, D = JSON.parse(document.getElementById('bjt-data').textContent), c = '日';
    const w = D.words.find(x => { const u = [...new Set(x.kj || [])]; return u.length === 1 && u[0] === c; });
    const saved = t.KC[c]; delete t.KC[c];
    const h = t.kzBodyHTML(c), st = t.storyHTML(w, 's-story');
    t.KC[c] = saved;
    const a = window.kzCardHTML, m = window.kzMark; window.kzCardHTML = undefined; window.kzMark = undefined;
    let h2 = '', st2 = '', err = '';
    try { h2 = t.kzBodyHTML(c); st2 = t.storyHTML(w, 's-story'); } catch (e) { err = String(e); }
    window.kzCardHTML = a; window.kzMark = m;
    return { w: w.w, simple: h.includes('kz-simple') && h.includes('kzu-ws') && h.includes('구성 · 풀이') && !/undefined|NaN/.test(h), oldRow: st.includes('class="lk-x"') && !st.includes('lk-hook') && st.includes('data-c="日"'),
      noScript: !err && h2.includes('kz-simple') && st2.includes('lk-hook') && !st2.includes('**') && !/undefined|NaN/.test(h2 + st2), err };
  });
  ok(fb.simple && fb.oldRow, 'kanji without a card: simple card (구성 · 풀이 + words) and old 구성 + 풀이 row on ' + fb.w);
  ok(fb.noScript, 'card script missing: simple card + plain hook, no error ' + fb.err);
  const samples = await page.evaluate(() => {
    const t = __t, KD = JSON.parse(document.getElementById('bjt-data').textContent).kanji, cs = Object.keys(t.KC);
    const by = f => cs.slice().sort((a, b) => f(b) - f(a))[0];
    const out = [by(c => KD[c].u.length), by(c => t.KC[c].hook.length + (t.KC[c].br || '').length), by(c => t.KC[c].t.length * 10 + Math.max(0, ...t.KC[c].t.map(s => s.pa.length))), by(c => KD[c].h.length), by(c => Math.max(...t.KC[c].p.map(p => p.cap.length))), '話', t.KZO.find(c => !t.KC[c])];
    return [...new Set(out.filter(c => c && KD[c]))];
  });
  await ctx.close();
  for (const vp of [{ width: 1180, height: 820 }, { width: 820, height: 1180 }, { width: 390, height: 844 }]) {
    const { ctx, page, errs } = await newPage(vp);
    await page.waitForSelector('#v-home details.gf', { state: 'attached' });
    let worst = 0, at = '';
    for (const c of samples) {
      await openKzT(page, c); await page.waitForSelector('#sheet:not([hidden]) .kz-card'); await page.waitForTimeout(120);
      const o = await overT(page, '#sheet-body'); if (o > worst) { worst = o; at = c; }
      if (c === samples[0]) await page.screenshot({ path: `/home/claude/work/app/shot_kz_sheet_${vp.width}.png` });
      await vis(page, '#sheet .sheet-head [data-act="closeSheet"]').click(); await page.waitForTimeout(80);
    }
    ok(worst <= 1, `kanji card sheet: no horizontal overflow ${vp.width}x${vp.height} (${samples.join('')})` + (worst > 1 ? ' worst ' + at + ' +' + worst + 'px' : ''));
    // 한자 단원 화면: 표본 한자로 장을 채워 앞면·해설
    await page.evaluate(sm => { const t = __t, k = t.KZCH[0].key; t.KZ.ch[k] = { n: 0, cur: { ord: sm, pos: 0, unk: [], ph: 'main', q: [], qpos: 0, next: [], round: 0, shuf: true, t: 0, k: 0, started: 1, u: 1 }, t: 0, last: null, u: 1 }; document.querySelector('#v-home details[data-g="kz"]').open = true; }, samples);
    await vis(page, '#v-home .kzu-book[data-k="0"]').click(); await page.waitForSelector('#v-kz .cf-word'); await page.waitForTimeout(350);
    let ow = 0, oat = '';
    for (let i = 0; i < samples.length; i++) {
      const f = await overT(page, '#kz-sc'); if (f > ow) { ow = f; oat = samples[i] + ' front'; }
      if (i === 0) await page.screenshot({ path: `/home/claude/work/app/shot_kz_front_${vp.width}.png` });
      await vis(page, '#v-kz [data-act="kzExplain"]').click(); await page.waitForTimeout(380);
      const e = await overT(page, '#kz-sc'); if (e > ow) { ow = e; oat = samples[i] + ' explain'; }
      const bar = await overT(page, '#v-kz .abar'); if (bar > ow) { ow = bar; oat = samples[i] + ' bar'; }
      if (i === 0) await page.screenshot({ path: `/home/claude/work/app/shot_kz_study_${vp.width}.png` });
      if (i < samples.length - 1) { await vis(page, '#v-kz [data-act="kzOk"]').click(); await page.waitForTimeout(380); }
    }
    ok(ow <= 1, `kanji unit screen (front + 해설): no horizontal overflow ${vp.width}x${vp.height}` + (ow > 1 ? ' worst ' + oat + ' +' + ow + 'px' : ''));
    await vis(page, '#v-kz [data-act="kzExit"]').click(); await page.waitForSelector('#v-home details[data-g="kz"]', { state: 'attached' });
    ok(await overT(page, '#v-home .scroll') <= 1, `home with the kanji fold open: no horizontal overflow ${vp.width}`);
    ok(errs.length === 0, `no console errors (kanji layout ${vp.width}): ` + errs.join(' | '));
    await ctx.close();
  }
}
await browser.close();
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
