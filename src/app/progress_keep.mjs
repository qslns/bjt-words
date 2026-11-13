// 진도 보존 시험(11/13, 확장 P1-3 — P2·P3 배포 전에도 씀)
// 같은 주소(BASE)에서 ① 지금 배포본(OLD)으로 진도를 만든다 → ② 새 빌드(NEW)로 바꿔 연다 → ③ (되돌리기 대비) 다시 OLD로 연다
//   ①: 가짜 진도(장 끝냄·진행 중·복습 단계·총정리·단어 기록·약점·★·약점 복습·가볍게 1회독·한자 단원)를 넣고,
//       화면으로도 진도를 만든다(기본 장·본편 장 몇 장 풀기, ★, 설정 2개, 한자 단원 몇 장)
//   ②: 저장된 값이 바이트까지 그대로인지(새 빌드가 열면서 다시 쓰지 않음), 장마다 진도가 장 키로 그대로 이어지는지,
//       없어진 장(키가 바뀐 장)이 EXPECT_GONE과 정확히 같은지, 단어 기록·약점·설정·한자 기록·이어서 하기·홈 숫자가 같은지
//   ③: 새 빌드가 저장한 걸 옛 빌드가 읽어도 오류 없음, 두 빌드에 다 있는 장 진도는 그대로
// 쓰기: OLD=옛 index.html NEW=새 index.html EXPECT_GONE='B:751-885:step,B:501-885:review,B:1-885:all' node progress_keep.mjs
//   EXPECT_GONE 표기: (B 기본 | P 본편):시작-끝:종류(step|review|all). 기본값 '' = 아무 장도 안 바뀜(P1)
import { chromium } from 'playwright';
import fs from 'fs';
const BASE = process.env.BASE || 'http://127.0.0.1:8765/';
const OLD = process.env.OLD || '/home/claude/bjt-words/index.html';
const NEW = process.env.NEW || '/home/claude/work/app/test/index.html';
const EXPECT_GONE = (process.env.EXPECT_GONE || '').split(',').map(s => s.trim()).filter(Boolean).sort();
/* 11/14 K1: EXPECT_KZ_NEW=1 → 한자 칸 순서가 바뀌어 한자 장은 새로 시작(키가 바뀜) — 한자별 기록(w)·시간(g)은 그대로여야 함 */
const KZ_NEW = process.env.EXPECT_KZ_NEW === '1';
const kzWG = s => { const o = JSON.parse(s); return JSON.stringify({ w: o.w, g: o.g }); };
/* 설정 옮기기(마이그레이션)로 바뀌어도 되는 설정 키, 예: ALLOW_S=em (11/13 시험일 옮기기 em 4) */
const ALLOW_S = (process.env.ALLOW_S || '').split(',').map(s => s.trim()).filter(Boolean);
const sNorm = x => { if (!x) return x; const o = JSON.parse(x); for (const k of ALLOW_S.concat('u')) delete o[k]; return JSON.stringify(o); };
const sDiff = (a, b) => { const x = JSON.parse(a || '{}'), y = JSON.parse(b || '{}'); return [...new Set(Object.keys(x).concat(Object.keys(y)))].filter(k => JSON.stringify(x[k]) !== JSON.stringify(y[k])).map(k => k + ':' + JSON.stringify(x[k]) + '→' + JSON.stringify(y[k])).join(' '); };
const SHOT = process.env.SHOT || '';
const html = { old: fs.readFileSync(OLD, 'utf8'), new: fs.readFileSync(NEW, 'utf8') };
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) { pass++; console.log('  ok  ', m); } else { fail++; console.log('  FAIL', m); } };
const buildOf = h => (/BUILD = '([^']*)'/.exec(h) || [])[1];
console.log('OLD', OLD, buildOf(html.old), '\nNEW', NEW, buildOf(html.new), '\nEXPECT_GONE', EXPECT_GONE.join(',') || '(없음)');

const browser = await chromium.launch({ ...(process.env.PW_CHROME ? { executablePath: process.env.PW_CHROME } : {}) }).catch(() => chromium.launch());
const ctx = await browser.newContext({ viewport: { width: 1180, height: 820 }, serviceWorkers: 'block' });
await ctx.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
let which = 'old';
await ctx.route(u => { const p = new URL(u).pathname; return p === '/' || p === '/index.html'; }, r => r.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: html[which] }));
const errs = { old: [], new: [], old2: [] };
async function open(w, tag) {
  which = w;
  const page = await ctx.newPage();
  page.on('pageerror', e => errs[tag].push(String(e)));
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource|fonts\.g/.test(m.text())) errs[tag].push(m.text()); });
  await page.goto(BASE + '?t=' + Date.now());
  await page.waitForSelector('#v-home .wk-top', { timeout: 60000 }); await page.waitForTimeout(300);
  return page;
}
const vis = (page, sel) => page.locator(sel + ' >> visible=true').first();
const openFolds = page => page.evaluate(() => document.querySelectorAll('#v-home details.gf').forEach(d => { d.open = true; }));
async function openBook(page, i) { await openFolds(page); await page.waitForTimeout(80); await vis(page, '#v-home .book[data-i="' + i + '"]').click({ position: { x: 30, y: 30 } }); await page.waitForSelector('#v-study .cf-word'); await page.waitForTimeout(380); }
async function tapAct(page, act) { await vis(page, '#v-study [data-act="' + act + '"]').click(); await page.waitForTimeout(380); }
const exitStudy = async page => { await vis(page, '[data-act="exit"]').click(); await page.waitForSelector('#v-home .wk-top'); await page.waitForTimeout(200); };

/* 앱 안에서 본 진도(장 키 기준) */
const snap = page => page.evaluate(() => {
  const t = __t, H = t.H, S = t.S, KZ = t.KZ;
  const chap = {}, desc = {};
  for (const c of t.CHAPTERS) { desc[c.key] = (c.basic ? 'B:' : 'P:') + c.a + '-' + c.b + ':' + c.kind; const x = H.ch[c.i]; if (x) chap[c.key] = JSON.stringify({ n: x.n, cur: x.cur, t: x.t, last: x.last, u: x.u }); }
  const ids = Object.keys(H.w).map(Number);
  const q = s => { const e = document.querySelector(s); return e ? e.textContent.replace(/\s+/g, ' ').trim() : ''; };
  return {
    raw: { h: localStorage.getItem('bjt500.hoedok.v2'), s: localStorage.getItem('bjt500.prefs.v2'), k: localStorage.getItem('bjt500.kanji.v1') },
    chap, desc, keys: t.CHAPTERS.map(c => c.key), nCh: t.CHAPTERS.length,
    w: JSON.stringify(H.w), wr: JSON.stringify(H.wr), wru: H.wru, lt: JSON.stringify({ pos: H.lt.pos, done: H.lt.done, t: H.lt.t }), g: JSON.stringify(H.g),
    S: JSON.stringify(S), KZ: JSON.stringify(KZ), kzKeys: t.KZCH.map(c => c.key),
    weak: ids.filter(t.isWeak).sort((a, b) => a - b).join(','), nW: JSON.parse(document.getElementById('bjt-data').textContent).words.length,
    banner: q('#v-home .resume'), stats: q('#v-home .stats'), wk: q('#v-home .wk-top .wk-h'), kzSum: q('#v-home details[data-g="kz"] > summary')
  };
});
const runOf = page => page.evaluate(() => { const r = __t.getRun(); return { id: __t.ui.id, run: r ? JSON.stringify({ ord: r.ord, pos: r.pos, unk: r.unk, ph: r.ph, q: r.q, qpos: r.qpos, next: r.next, round: r.round, k: r.k }) : null, bar: document.querySelector('#v-study .sb-t') ? document.querySelector('#v-study .sb-t').textContent : '' }; });

// ---------- ① 옛 빌드: 진도 만들기 ----------
let p = await open('old', 'old');
const C = await p.evaluate(() => __t.CHAPTERS.map(c => ({ i: c.i, key: c.key, basic: !!c.basic, kind: c.kind, a: c.a, b: c.b, ids: c.ids })));
const KZC = await p.evaluate(() => __t.KZCH.map(c => ({ i: c.i, key: c.key, kind: c.kind, ids: c.ids })));
const main = C.filter(c => !c.basic), bas = C.filter(c => c.basic);
let seedN = 12345; const rnd = () => (seedN = (seedN * 1103515245 + 12345) % 2147483648) / 2147483648;
const ALL = [...new Set(C.flatMap(c => c.ids))];
const T0 = 1762900000000;   /* 고정 시각(11/12 무렵) → 결과가 매번 같게 */
const last = (k, tot, r) => ({ pass: 1, k, tot, r, t: 600000, at: T0 });
const run = (ids, pos, extra) => Object.assign({ ord: ids.slice(), pos, unk: ids.slice(0, Math.min(3, pos)), ph: 'main', q: [], qpos: 0, next: [], round: 0, shuf: true, t: 120000, k: Math.max(0, pos - 3), started: T0, u: T0 }, extra || {});
const ch = {}; let u = T0;
const put = (c, o) => { ch[c.i] = Object.assign({ n: 0, cur: null, t: 0, last: null, u: ++u, k: c.key }, o); };
// 본편: 1~4장 끝냄(여러 번), 6장(251–300) 끝냄, 1–500 총정리 1번, 13장(501–600) 진행 중(본 단계), 14장(501–650) 복습 단계, 전체 총정리 진행 중
[0, 1, 2, 3].forEach(i => put(main[i], { n: 1 + (i % 3), t: 900000, last: last(40 + i, main[i].ids.length, 2) }));
put(main[5], { n: 1, t: 1800000, last: last(270, main[5].ids.length, 3) });
const rev = main.find(c => c.kind === 'review'); if (rev) put(rev, { n: 1, t: 3600000, last: last(470, rev.ids.length, 4) });
if (main[12]) put(main[12], { n: 0, cur: run(main[12].ids, 23, { u: T0 + 5000 }), t: 400000 });
if (main[13]) { const q = main[13].ids.slice(5, 12); put(main[13], { n: 1, cur: run(main[13].ids, main[13].ids.length, { ph: 'loop', q, qpos: 2, next: q.slice(0, 2), round: 1, unk: q, u: T0 + 6000 }), t: 500000, last: last(80, 100, 2) }); }
const allM = main.find(c => c.kind === 'all'); if (allM) put(allM, { n: 0, cur: run(allM.ids, 7, { u: T0 + 4000 }), t: 100000 });
// 기본: 1~3장 끝냄, 5장(201–250 쪽) 진행 중, 기본 1–500 총정리 끝냄, 마지막 묶음(751– 쪽)의 장들·기본 총정리·기본 전체 총정리에도 진도(P2에서 바뀌는 장 시험용)
[0, 1, 2].forEach(i => put(bas[i], { n: 2, t: 700000, last: last(45, bas[i].ids.length, 1) }));
if (bas[4]) put(bas[4], { n: 0, cur: run(bas[4].ids, 31, { u: T0 + 3000 }), t: 300000 });
const bRev = bas.filter(c => c.kind === 'review'); bRev.forEach((c, j) => put(c, { n: 1, t: 2000000, last: last(400 + j, c.ids.length, 3) }));
const bLast = bas.filter(c => c.kind === 'step' && c.a > 500).slice(-3); bLast.forEach((c, j) => put(c, j === bLast.length - 1 ? { n: 1, cur: run(c.ids, 4, { u: T0 + 2000 }), t: 200000, last: last(30, c.ids.length, 1) } : { n: 1, t: 200000, last: last(30, c.ids.length, 1) }));
const allB = bas.find(c => c.kind === 'all'); if (allB) put(allB, { n: 1, t: 4000000, last: last(800, allB.ids.length, 5) });
// 단어 기록: 900개(본편·기본만 섞임) · 약점(많이 틀림) · ★ · 약점에서 뺀 것(rm)
const w = {};
for (let j = 0; j < 900; j++) { const id = ALL[Math.floor(rnd() * ALL.length)]; const m = Math.floor(rnd() * 8); w[id] = { n: 1 + Math.floor(rnd() * 5), m, l: rnd() < .6 ? 1 : 0, t: Math.floor(rnd() * 90000), pin: rnd() < .03 ? 1 : 0, rm: m >= 5 && rnd() < .3 ? m - 1 : -1, u: T0 - j * 1000 }; }
const weakSeed = Object.keys(w).map(Number).filter(id => w[id].pin || w[id].m - Math.max(0, w[id].rm) >= 5);
const H = { ch, w, wr: weakSeed.length > 3 ? run(weakSeed.slice(0, 20), 2, { u: T0 + 1000 }) : null, wru: T0 + 1000, g: { tt: 98765432, d: { '2026-11-10': 3600000, '2026-11-11': 7200000, '2026-11-12': 1800000 } }, lt: { pos: 37, done: 1, t: 4000000, u: T0, id: main[0].ids[37] }, lay: 'v4', rs: 0, u: T0 + 9000 };
// 한자 단원: 1장 끝냄, 2장 진행 중, 한자 기록 120자
const kw = {}; [...new Set(KZC.flatMap(c => c.ids))].slice(0, 120).forEach((c, j) => { kw[c] = { n: 1 + (j % 3), m: j % 4, l: j % 3 ? 1 : 0, t: 5000, u: T0 - j }; });
const KZ = { ch: { [KZC[0].key]: { n: 1, cur: null, t: 600000, last: last(44, 50, 2), u: T0 }, [KZC[1].key]: { n: 0, cur: run(KZC[1].ids, 9, { unk: KZC[1].ids.slice(0, 2) }), t: 100000, last: null, u: T0 + 1 } }, w: kw, g: { tt: 700000, d: { '2026-11-11': 700000 } }, u: T0 };
await p.evaluate(([h, k]) => { localStorage.setItem('bjt500.hoedok.v2', h); localStorage.setItem('bjt500.kanji.v1', k); }, [JSON.stringify(H), JSON.stringify(KZ)]);
await p.close();
p = await open('old', 'old');
const seeded = await snap(p);
ok(Object.keys(seeded.chap).length === Object.keys(ch).length, 'old build reads every seeded chapter by key: ' + Object.keys(seeded.chap).length + '/' + Object.keys(ch).length);
// 화면으로: 기본 1장 몇 장(알고있음·모르겠음) → 나감 · 본편 2장 몇 장 + ★ → 나감 · 설정 2개 · 한자 단원 2장 이어서 몇 장
await openBook(p, bas[0].i);
for (const a of ['ok', 'ng', 'next', 'ok', 'ok']) await tapAct(p, a);
await exitStudy(p);
await openBook(p, main[1].i);
await tapAct(p, 'ok'); const r0 = await p.evaluate(() => ({ star: __t.ui.id, was: __t.isWeak(__t.ui.id) })); await tapAct(p, 'star'); r0.now = await p.evaluate(id => __t.isWeak(id), r0.star); await tapAct(p, 'ok'); await tapAct(p, 'ng'); await tapAct(p, 'next');
await exitStudy(p);
await vis(p, '[data-act="settings"]').click(); await p.waitForTimeout(200);
await vis(p, '#sheet [data-act="setWk"][data-v="3"]').click(); await p.waitForTimeout(200);
await p.fill('#exam-date', '2027-02-21'); await p.dispatchEvent('#exam-date', 'change'); await p.waitForTimeout(200);
await vis(p, '#sheet .sheet-head [data-act="closeSheet"]').click(); await p.waitForTimeout(150);
await p.evaluate(() => { const d = document.querySelector('#v-home details[data-g="kz"]'); if (d) d.open = true; });
await vis(p, '#v-home .kzu-book[data-k="1"]').click(); await p.waitForSelector('#v-kz .cf-word'); await p.waitForTimeout(380);
for (const a of ['kzOk', 'kzNg', 'kzNext', 'kzOk']) { const l = p.locator('#v-kz [data-act="' + a + '"] >> visible=true'); if (await l.count()) { await l.first().click(); await p.waitForTimeout(380); } }
await vis(p, '#v-kz [data-act="kzExit"]').click(); await p.waitForSelector('#v-home .wk-top'); await p.waitForTimeout(200);
// 이어서 하기 → 지금 카드·진행 상태 기록 → 그대로 나감
await vis(p, '#v-home .resume').click(); await p.waitForSelector('#v-study .cf-word, #v-kz .cf-word'); await p.waitForTimeout(380);
const r1 = await runOf(p);
await exitStudy(p);
const s1 = await snap(p);
if (SHOT) await p.screenshot({ path: SHOT + '_old.png' });
ok(errs.old.length === 0, 'no console errors in the old build: ' + errs.old.join(' | '));
const made = { wkN: s1.S.includes('"wkN":3'), exam: s1.S.includes('"exam":"2027-02-21"'), weak: s1.weak.split(',').length, kzw: Object.keys(JSON.parse(s1.KZ).w).length, star: r0.now !== r0.was && JSON.parse(s1.raw.h).w[r0.star].pin === (r0.now ? 1 : 0) };
ok(made.wkN && made.exam && made.weak >= 3 && made.kzw >= 120 && made.star, 'old build: progress made by the UI too (settings 3번·시험일, ★ toggled on a card, ' + made.weak + ' weak, ' + made.kzw + ' kanji records, resume ' + s1.banner + '): ' + JSON.stringify(made));
await p.close();

// ---------- ② 새 빌드: 그대로 이어지는지 ----------
p = await open('new', 'new');
const s2 = await snap(p);
ok(s2.raw.h === s1.raw.h && s2.raw.k === s1.raw.k && (s2.raw.s === s1.raw.s || (ALLOW_S.length && sNorm(s2.raw.s) === sNorm(s1.raw.s))), 'stored progress is byte-identical after opening the new build (nothing rewritten on load)' + (s2.raw.s !== s1.raw.s ? ' — settings moved: ' + sDiff(s1.raw.s, s2.raw.s) + ' (ALLOW_S=' + ALLOW_S.join(',') + ')' : ''));
const gone = Object.keys(s1.desc).filter(k => !s2.keys.includes(k)).map(k => s1.desc[k]).sort();
const added = s2.keys.filter(k => !(k in s1.desc)).map(k => s2.desc[k]).sort();
ok(gone.join(',') === EXPECT_GONE.join(','), 'chapters whose key changed = expected: [' + gone.join(',') + '] (new chapters: ' + (added.join(',') || '-') + ')');
const kept = Object.keys(s1.chap).filter(k => s2.keys.includes(k)), lost = Object.keys(s1.chap).filter(k => !s2.keys.includes(k));
const diff = kept.filter(k => s2.chap[k] !== s1.chap[k]);
ok(diff.length === 0 && kept.every(k => k in s2.chap), 'every chapter progress kept by key: ' + kept.length + ' chapters' + (lost.length ? ' (gone with their chapter: ' + lost.map(k => s1.desc[k]).join(',') + ')' : '') + (diff.length ? ' DIFF ' + diff.map(k => s1.desc[k]).join(',') : ''));
ok(s2.w === s1.w && s2.wr === s1.wr && s2.wru === s1.wru && s2.lt === s1.lt && s2.g === s1.g, 'word records · weak review run · light pass · time totals identical');
ok(s2.weak === s1.weak && s2.wk === s1.wk, 'weak words identical: ' + s2.wk);
ok(s2.S === s1.S || (ALLOW_S.length && sNorm(s2.S) === sNorm(s1.S)), 'settings identical' + (s2.S !== s1.S ? ' except ' + sDiff(s1.S, s2.S) : ''));
if (!KZ_NEW) ok(s2.KZ === s1.KZ && s2.kzSum === s1.kzSum && s2.kzKeys.join() === s1.kzKeys.join(), 'kanji unit records identical: ' + s2.kzSum);
else ok(kzWG(s2.KZ) === kzWG(s1.KZ) && s2.kzKeys.join() !== s1.kzKeys.join() && JSON.parse(s1.KZ).w && Object.keys(JSON.parse(s1.KZ).w).length > 0, 'K1: kanji chapters start fresh with the new order (' + s1.kzKeys.length + ' → ' + s2.kzKeys.length + ' chapters: ' + s2.kzSum + '), per-kanji records (' + Object.keys(JSON.parse(s2.KZ).w).length + ') and time kept');
const resumeLost = lost.some(k => JSON.parse(s1.chap[k]).cur);
ok(resumeLost || s2.banner === s1.banner, 'resume banner identical: ' + s2.banner);
/* 홈 통계: 본 단어 n/전체 단어 수 · 앎 · 끝낸 장 n/장 수 · 오늘 · 총 — 전체 단어 수·장 수는 새 빌드 것, 끝낸 장은 없어진 장만큼 줄어듦 */
const st = x => x.replace(/본 단어 (\d+)\/\d+/, '본 단어 $1').replace(/끝낸 장 \d+\/\d+/, '');
const doneOf = s => +(/끝낸 장 (\d+)\//.exec(s.stats) || [])[1];
const goneDone = lost.filter(k => JSON.parse(s1.chap[k]).n > 0).length;
ok(st(s2.stats) === st(s1.stats) && doneOf(s2) === doneOf(s1) - goneDone && s2.stats.includes('/' + s2.nCh) && s2.stats.includes('/' + s2.nW), 'home stats same (본 단어·앎·오늘·총 그대로, 끝낸 장 ' + doneOf(s1) + ' → ' + doneOf(s2) + ' = 없어진 장 ' + goneDone + '개만큼, 장 ' + s1.nCh + ' → ' + s2.nCh + ', 단어 ' + s1.nW + ' → ' + s2.nW + ')');
if (!resumeLost) {
  await vis(p, '#v-home .resume').click(); await p.waitForSelector('#v-study .cf-word, #v-kz .cf-word'); await p.waitForTimeout(380);
  const r2 = await runOf(p);
  ok(r2.id === r1.id && r2.run === r1.run && r2.bar === r1.bar, 'resume continues on the same card with the same run (' + r2.bar.trim() + ', card ' + r2.id + ')');
  await exitStudy(p);
}
// 새 빌드에서 조금 더 공부 → 저장 (③에서 옛 빌드가 읽음)
const later = main.find(c => c.kind === 'step' && !(c.i in ch));
await openBook(p, later.i); await tapAct(p, 'ok'); await tapAct(p, 'ok'); await exitStudy(p);
const s3 = await snap(p);
if (SHOT) await p.screenshot({ path: SHOT + '_new.png' });
ok(errs.new.length === 0, 'no console errors in the new build: ' + errs.new.join(' | '));
await p.close();

// ---------- ③ 되돌리기 대비: 새 빌드가 저장한 걸 옛 빌드가 읽음 ----------
p = await open('old', 'old2');
const s4 = await snap(p);
const both = Object.keys(s3.chap).filter(k => s1.keys.includes(k));
const d4 = both.filter(k => s4.chap[k] !== s3.chap[k]);
ok(d4.length === 0 && s4.w === s3.w && (s4.S === s3.S || (ALLOW_S.length && sNorm(s4.S) === sNorm(s3.S))) && (KZ_NEW ? kzWG(s4.KZ) === kzWG(s3.KZ) : s4.KZ === s3.KZ), 'old build reads what the new build saved: ' + both.length + ' chapters, word records, settings, kanji' + (d4.length ? ' DIFF ' + d4.map(k => s3.desc[k]).join(',') : ''));
ok(errs.old2.length === 0, 'no console errors when going back to the old build: ' + errs.old2.join(' | '));
await p.close();
await browser.close();
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
