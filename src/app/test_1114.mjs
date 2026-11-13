// 11/14 시험: 묶음별 약점 · 카드 표시 겹치기 · 기본 순서 · (LV_BASE가 있으면) N3·N2 칸
// 쓰기: DATA=…/data_app.json [LV_BASE=http://127.0.0.1:8766/ LV_DATA=…/data_lv.json] node test_1114.mjs
import { chromium } from 'playwright';
import fs from 'fs';
const BASE = process.env.BASE || 'http://127.0.0.1:8765/';
const data = JSON.parse(fs.readFileSync(process.env.DATA || '/home/claude/work/build/data_app.json', 'utf8'));
const ORDER = data.words.filter(w => w.ord != null).sort((a, b) => a.ord - b.ord).map(w => w.id);
const BORDER = data.words.filter(w => w.bn != null).sort((a, b) => a.bn - b.bn).map(w => w.id);
const NOS = new Set(ORDER);
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) { pass++; console.log('  ok  ', m); } else { fail++; console.log('  FAIL', m); } };
const browser = await chromium.launch({ ...(process.env.PW_CHROME ? { executablePath: process.env.PW_CHROME } : {}) });
async function newPage(base, init, vp) {
  const ctx = await browser.newContext({ viewport: vp || { width: 1180, height: 820 }, serviceWorkers: 'block' });
  const page = await ctx.newPage(); const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource|fonts\.g/.test(m.text())) errs.push(m.text()); });
  await page.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
  if (init) await page.addInitScript(init);
  await page.goto(base); await page.waitForSelector('#v-home .book', { state: 'attached' });
  return { ctx, page, errs };
}
const seed = h => `(() => { if (sessionStorage.getItem('seeded')) return; sessionStorage.setItem('seeded','1'); localStorage.setItem('bjt500.hoedok.v2', ${JSON.stringify(JSON.stringify(h))}); })();`;
const H0 = w => ({ ch: {}, w: w || {}, wr: null, wru: 0, g: { tt: 0, d: {} }, lt: { pos: 0, done: 0, t: 0, u: 1 }, lay: 'v4', rs: 0, u: 1 });
const pin = (ids) => Object.fromEntries(ids.map(id => [id, { n: 1, m: 0, l: 0, t: 0, pin: 1, rm: -1, u: 1 }]));
const openFold = async (page, key) => { await page.evaluate(k => { const d = document.querySelector('#v-home details.gf[data-g="' + k + '"]'); if (d) d.open = true; }, key); await page.waitForTimeout(50); };

// ---------- 1. 기본 순서 ----------
{
  const exp = data.words.filter(w => w.bn != null).sort((a, b) => a.bn - b.bn).slice(0, 5).map(w => w.w);
  ok(exp.join(',') === 'ない,する,いる,ある,〜人', '기본 맨 앞 5개: ' + exp.join(','));
  const { ctx, page, errs } = await newPage(BASE);
  const ch = await page.evaluate(() => { const c = window.__t.CHAPTERS.find(c => c.basic); return { a: c.a, b: c.b, ids: c.ids.slice(0, 3) }; });
  ok(ch.a === 1 && ch.b === 50 && ch.ids.join() === BORDER.slice(0, 3).join(), '基本1章 = 새 기본 1–50');
  ok(errs.length === 0, 'no errors (기본 순서) ' + errs.slice(0, 2).join(' | '));
  await ctx.close();
}

// ---------- 2. 묶음별 약점 ----------
{
  const b0 = BORDER.slice(0, 500).filter(id => !NOS.has(id)).slice(10, 13);   // 기본 1 묶음, 기본에만 있는 단어 3개
  const p0 = ORDER.slice(0, 500).filter(id => !BORDER.includes(id)).slice(5, 7); // 1부, BJT에만 있는 단어 2개
  const b1 = BORDER.slice(500, 1000).filter(id => !NOS.has(id)).slice(0, 1);
  const all = b0.concat(p0, b1);
  const { ctx, page, errs } = await newPage(BASE, seed(H0(pin(all))));
  await openFold(page, 'B'); await openFold(page, 'b0');
  const pwT = await page.textContent('#v-home details.gf[data-g="b0"] .pw');
  ok(pwT.includes('약점 3개'), '기본 1 묶음 약점 줄: ' + pwT.slice(0, 30));
  const sumT = await page.textContent('#v-home details.gf[data-g="b0"] > summary');
  ok(sumT.includes('★ 3'), '접기 머리에 ★ 3: ' + sumT.replace(/\s+/g, ' ').slice(0, 60));
  const sumB1 = await page.textContent('#v-home details.gf[data-g="b1"] > summary');
  ok(sumB1.includes('★ 1') && !(await page.textContent('#v-home details.gf[data-g="b2"] > summary')).includes('★'), '기본 2 ★ 1 · 기본 3 ★ 없음');
  ok((await page.textContent('#v-home .wk-top')).includes('6개'), '맨 위 전체 약점은 6개 그대로');
  await page.click('#v-home details.gf[data-g="b0"] .pw [data-act="weakNew"]');
  await page.waitForSelector('#v-study .sbar', { state: 'visible' });
  const t1 = await page.textContent('#v-study .sbar .sb-t');
  ok(t1.includes('약점 복습 · 기본 1'), '복습 화면 제목: ' + t1.slice(0, 30));
  const run = await page.evaluate(() => { const r = window.__t.getRun(); return r && r.ord; });
  ok(run && run.length === 3 && run.every(id => b0.includes(id)), '복습 카드 = 기본 1의 약점 3개만');
  ok(await page.evaluate(() => !!window.__t.H.wrp.b0 && !window.__t.H.wr), '진행은 H.wrp.b0에(전체 약점 진행 H.wr은 안 건드림)');
  await page.click('#v-study .sbar [data-act="exit"]'); await page.waitForTimeout(150);
  const rs = await page.textContent('#v-home .resume');
  ok(rs.includes('약점 복습 · 기본 1'), '홈 이어서 하기: ' + rs.replace(/\s+/g, ' ').slice(0, 40));
  await page.click('#v-home .resume'); await page.waitForSelector('#v-study .sbar', { state: 'visible' });
  ok((await page.textContent('#v-study .sbar .sb-t')).includes('기본 1'), '이어서 하기 → 같은 묶음 약점 복습');
  await page.click('#v-study .sbar [data-act="exit"]'); await page.waitForTimeout(150);
  await openFold(page, 'B'); await openFold(page, 'b0');
  await page.click('#v-home details.gf[data-g="b0"] .pw [data-act="weakView"]');
  await page.waitForSelector('#v-weak .bar-title', { state: 'visible' });
  const wt = await page.textContent('#v-weak .bar-title'), wn = await page.locator('#wlist li').count();
  ok(wt.includes('기본 1') && wt.includes('3') && wn === 3, '묶음 약점 목록: ' + wt + ' · ' + wn + '줄');
  await page.click('#v-weak [data-act="weakView"][data-pg=""]'); await page.waitForTimeout(100);
  ok((await page.textContent('#v-weak .bar-title')).trim() === '약점 단어 6' && await page.locator('#wlist li').count() === 6, '전체 약점 보기 → 6');
  // 1부 묶음 약점 2개
  await page.click('#v-weak .bar [data-act="home"]'); await page.waitForTimeout(100);
  await openFold(page, 'P'); await openFold(page, 'p0');
  ok((await page.textContent('#v-home details.gf[data-g="p0"] .pw')).includes('약점 2개'), '1부 묶음 약점 2개');
  // 약점 없는 묶음: 버튼 꺼짐
  await openFold(page, 'b2');
  ok(await page.locator('#v-home details.gf[data-g="b2"] .pw [data-act="weakNew"][disabled]').count() === 1, '약점 없는 묶음은 복습 버튼 꺼짐');
  // 새로고침해도 묶음 진행 유지
  await page.reload(); await page.waitForSelector('#v-home .book', { state: 'attached' });
  ok(await page.evaluate(() => !!window.__t.H.wrp.b0 && window.__t.H.wrp.b0.ord.length === 3), '새로고침 뒤에도 H.wrp.b0 유지');
  ok(errs.length === 0, 'no errors (묶음별 약점) ' + errs.slice(0, 2).join(' | '));
  await ctx.close();
}

// ---------- 3. 카드 표시 ----------
{
  const both = data.words.find(w => w.bn != null && w.ord != null), bOnly = data.words.find(w => w.bn != null && w.ord == null), mOnly = data.words.find(w => w.ord != null && w.bn == null);
  const { ctx, page, errs } = await newPage(BASE);
  const tags = async id => { await page.evaluate(id => { const b = document.createElement('button'); b.dataset.act = 'open'; b.dataset.id = id; document.body.appendChild(b); b.click(); b.remove(); }, id); await page.waitForTimeout(120); const t = await page.$$eval('#sheet-body .ans-top .tb-t', a => a.map(x => x.textContent)); await page.evaluate(() => { const b = document.querySelector('#sheet [data-act="closeSheet"]'); if (b) b.click(); }); return t.join('|'); };
  const t1 = await tags(both.id), t2 = await tags(bOnly.id), t3 = await tags(mOnly.id);
  ok(t1 === '기본|BJT ' + both.t, '기본+BJT 카드: ' + t1);
  ok(t2 === '기본', '기본만: ' + t2);
  ok(t3 === 'BJT ' + mOnly.t, 'BJT만: ' + t3);
  ok(errs.length === 0, 'no errors (표시) ' + errs.slice(0, 2).join(' | '));
  await ctx.close();
}

// ---------- 4. N3·N2 칸 (가짜 데이터 빌드) ----------
if (process.env.LV_BASE) {
  const LB = process.env.LV_BASE, ld = JSON.parse(fs.readFileSync(process.env.LV_DATA, 'utf8'));
  const n3 = ld.words.filter(w => w.jl === 3).length, n2 = ld.words.filter(w => w.jl === 2).length;
  const keysOf = async base => { const { ctx, page } = await newPage(base); const k = await page.evaluate(() => window.__t.CHAPTERS.filter(c => !c.lv).map(c => c.key)); await ctx.close(); return k; };
  const k0 = await keysOf(BASE), k1 = await keysOf(LB);
  ok(k0.length > 0 && JSON.stringify(k0) === JSON.stringify(k1), 'N3·N2를 넣어도 BJT·기본 장 키는 그대로 (' + k0.length + ')');
  const pinN3 = ld.words.filter(w => w.jl === 3 && w.jn <= 500).slice(3, 5).map(w => w.id);
  const { ctx, page, errs } = await newPage(LB, seed(H0(pin(pinN3))));
  const hasL3 = await page.locator('#v-home details.gf[data-g="L3"]').count(), hasL2 = await page.locator('#v-home details.gf[data-g="L2"]').count();
  ok(hasL3 === 1 && hasL2 === 1, 'N3 단어 · N2 단어 접기');
  const order = await page.evaluate(() => [...document.querySelectorAll('#v-home details.gf[data-g]')].map(d => d.dataset.g).filter(g => /^[BPLk]/.test(g)));
  ok(order.join(',').startsWith('B,P,L3,L2'), '홈 순서 기본 → BJT → N3 → N2: ' + order.join(','));
  await openFold(page, 'L3'); await openFold(page, 'l3_0'); await openFold(page, 'l3_1');
  const s0 = await page.textContent('#v-home details.gf[data-g="l3_0"] > summary');
  ok(s0.includes('N3 1부') && s0.includes('N3 1–' + Math.min(500, n3)) && s0.includes('★ 2'), 'N3 1부 머리: ' + s0.replace(/\s+/g, ' ').slice(0, 70));
  if (n3 > 500) ok((await page.textContent('#v-home details.gf[data-g="l3_1"] > summary')).includes('N3 501–' + n3), 'N3 2부 범위');
  const names = await page.$$eval('#v-home details.gf[data-g="l3_0"] .book .b-ch', a => a.map(x => x.textContent));
  const expN = await page.evaluate(() => window.__t.CHAPTERS.filter(c => c.lv === 3 && c.part === 0 && c.kind !== 'all').length);
  ok(names[0] === 'N3·1章' && names.length === expN && expN >= 11, 'N3 장 이름·수: ' + names.slice(0, 2).join(',') + ' … ' + names.length + ' (n3 ' + n3 + ')');
  const n2s = await page.textContent('#v-home details.gf[data-g="L2"] > summary');
  ok(n2s.includes('N2 단어') && n2s.includes('N2 1–' + n2), 'N2 머리: ' + n2s.replace(/\s+/g, ' ').slice(0, 50));
  const rs = await page.textContent('#v-home .resume');
  ok(rs.includes('基本1章'), '다음 순서는 기본부터: ' + rs.replace(/\s+/g, ' ').slice(0, 30));
  const i0 = await page.evaluate(() => window.__t.CHAPTERS.find(c => c.lv === 3).i);
  await page.click('#v-home .book[data-i="' + i0 + '"]'); await page.waitForSelector('#v-study .sbar', { state: 'visible' });
  const st = await page.textContent('#v-study .sbar .sb-t');
  ok(st.includes('N3·1章') && st.includes('N3 1–50'), 'N3 장 열기: ' + st.replace(/\s+/g, ' ').slice(0, 40));
  const cid = await page.evaluate(() => window.__t.ui.id);
  const tg = await page.$$eval('#v-study .cf-top .tb-t', a => a.map(x => x.textContent).join('|'));
  ok(/N3$/.test(tg), 'N3 카드 표시: ' + tg);
  const no = await page.textContent('#v-study .cf-top .no');
  ok(/N3 \d+/.test(no), '번호에 N3 순위: ' + no);
  await page.click('#v-study .sbar [data-act="exit"]'); await page.waitForTimeout(100);
  // 목록 거르기
  await page.evaluate(() => { const b = document.createElement('button'); b.dataset.act = 'browse'; document.body.appendChild(b); b.click(); b.remove(); });
  await page.waitForTimeout(200);
  const hasN3 = await page.locator('[data-act="bf"][data-grp="tier"][data-v="N3"]').count();
  if (hasN3) { await page.click('[data-act="bf"][data-grp="tier"][data-v="N3"]'); await page.waitForTimeout(200); const meta = await page.textContent('#bmeta'); ok(meta.includes(String(n3)), '목록 N3 거르기: ' + meta.slice(0, 30)); }
  else ok(false, '목록에 N3 거르기 버튼');
  ok(errs.length === 0, 'no errors (N3·N2) ' + errs.slice(0, 2).join(' | '));
  await ctx.close();
}
await browser.close();
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
