// 10/20 한자 소리 시험: 대표 소리(앞면 한자 탭·해설 자동·[발음]) · 읽기 칩(①②③, 흐린 칩) · 단어 카드에서 연 한자 카드 칩 · 음성 파일·버전
import { chromium } from 'playwright';
const BASE = process.env.BASE || 'http://127.0.0.1:8765/';
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) { pass++; console.log('  ok  ', m); } else { fail++; console.log('  FAIL', m); } };
const browser = await chromium.launch({ ...(process.env.PW_CHROME ? { executablePath: process.env.PW_CHROME } : {}) });
for (const vp of [{ width: 820, height: 1180 }, { width: 1180, height: 820 }]) {
  const ctx = await browser.newContext({ viewport: vp, serviceWorkers: 'block', hasTouch: true });
  const page = await ctx.newPage(); const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource|fonts\.g/.test(m.text())) errs.push(m.text()); });
  await page.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
  await page.goto(BASE + '?t=' + Date.now());
  await page.waitForSelector('#v-home details.gf', { state: 'attached', timeout: 60000 });
  const tag = vp.width + 'x' + vp.height;
  // 데이터: 카드마다 순위·흘려보기·대표 소리, 음성 파일 버전
  const dv = await page.evaluate(() => {
    const t = __t, bad = []; let chips = 0, sk = 0, k = 0, kr = 0;
    for (const c of t.KZO) {
      const card = t.KC[c];
      if (!card) { bad.push(c + ':no card'); continue; }
      const ranks = [...(card.onr || []), ...(card.kunr || [])].sort((a, b) => a - b);
      if (!ranks.length || ranks.some((r, i) => r !== i + 1)) bad.push(c + ':ranks ' + ranks.join(','));
      if (!Array.isArray(card.rep) || !card.rep.length) bad.push(c + ':rep');
      if (!t.AV[t.kzRepKey(c)]) bad.push(c + ':no rep audio'); else k++;
      for (const r of [...card.on, ...card.kun]) {
        const p = String(r).replace(/[()（）]/g, '');
        if (/っ$/.test(p)) continue;
        chips++;
        if (!t.AV[t.kzRdKey(p)]) bad.push(c + ':no audio ' + p);
      }
      sk += [...(card.ons || []), ...(card.kuns || [])].filter(Boolean).length;
      // 1순위는 흘려보기가 아님
      const all = [...card.on.map((r, i) => [card.onr[i], card.ons[i]]), ...card.kun.map((r, i) => [card.kunr[i], card.kuns[i]])];
      if (all.some(([r, s]) => r === 1 && s)) bad.push(c + ':rank1 gray');
      // 10/21 대표 소리 = 빨간(외울) 읽기를 순위대로, 빨강은 ①부터 이어지고 최대 3개
      const reds = [...card.on.map((r, i) => [card.onr[i], card.ons[i], r]), ...card.kun.map((r, i) => [card.kunr[i], card.kuns[i], r])].filter(x => !x[1]).sort((a, b) => a[0] - b[0]);
      if (reds.length < 1 || reds.length > 3 || reds.some((x, i) => x[0] !== i + 1)) bad.push(c + ':reds ' + reds.map(x => x[0]).join(','));
      if (JSON.stringify(reds.map(x => x[2])) !== JSON.stringify(card.rep)) bad.push(c + ':rep≠reds');
    }
    kr = Object.keys(t.AV).filter(x => x.startsWith('kr/')).length;
    return { n: t.KZO.length, bad: bad.slice(0, 12), nbad: bad.length, chips, sk, k, kr };
  });
  ok(dv.nbad === 0 && dv.k === 950, `${tag} 950 cards: ranks ①… complete, rep sound + reading audio for every chip (${dv.chips} chips, ${dv.kr} reading files, ${dv.sk} skim): ` + dv.bad.join(' | '));
  // 한자 단원 앞면: 큰 한자 = 버튼(누르면 대표 소리) + 안내, 자동 재생 없음
  await page.evaluate(() => { document.querySelector('#v-home details[data-g="kz"]').open = true; });
  await page.locator('#v-home .kzu-book[data-k="0"] >> visible=true').first().click();
  await page.waitForSelector('#v-kz .cf-word');
  await page.waitForTimeout(400);
  const c0 = await page.evaluate(() => __t.kui.c);
  const f0 = await page.evaluate(() => ({ src: __t.AUD.el ? __t.AUD.el.src : '', btn: document.querySelector('#v-kz .cf-word').tagName, act: document.querySelector('#v-kz .cf-word').dataset.act, hint: (document.querySelector('#v-kz .cf-hint') || {}).textContent || '' }));
  ok(f0.btn === 'BUTTON' && f0.act === 'kzSay' && f0.hint.includes('한자를 누르면 발음') && !f0.src, `${tag} front: kanji ${c0} is a tap-to-hear button + hint, nothing plays by itself`);
  await page.locator('#v-kz .cf-word').tap(); await page.waitForTimeout(500);
  const f1 = await page.evaluate(c => ({ src: __t.AUD.el ? __t.AUD.el.src : '', url: __t.kzAUrl(__t.kzRepKey(c)), mem: !!(__t.AMEM.m.get(__t.kzAUrl(__t.kzRepKey(c)))) }), c0);
  ok(f1.src && (f1.src === f1.url || f1.src.startsWith('blob:')) && f1.mem, `${tag} tap the front kanji → its representative sound (${f1.src.startsWith('blob:') ? 'from memory' : 'url'})`);
  ok(await page.evaluate(() => __t.kui.rev) === false, `${tag} tapping the kanji does not open the answer`);
  // 해설: 자동 1번 + [발음]
  await page.evaluate(() => { __t.AUD.stop(); if (__t.AUD.el) { __t.AUD.el.removeAttribute('src'); __t.AUD.el.load(); } });
  await page.locator('#v-kz [data-act="kzExplain"] >> visible=true').tap(); await page.waitForTimeout(500);
  const e1 = await page.evaluate(c => ({ src: __t.AUD.el ? __t.AUD.el.src : '', url: __t.kzAUrl(__t.kzRepKey(c)), bar: [...document.querySelectorAll('#v-kz .abar-in > *')].map(b => b.dataset.act || b.className).join(','), S: __t.S.auto }), c0);
  ok(e1.S === true && e1.src && (e1.src === e1.url || e1.src.startsWith('blob:')), `${tag} 해설 opens → representative sound plays once (자동 발음 on)`);
  ok(e1.bar === 'kzSay,kzNg,kzOk', `${tag} 해설 bar [발음][모르겠음][알고있음]`);
  // 읽기 칩: ①…, ①은 진하게(kz-r1) 하나, 흐린 칩(kz-sk), 누르면 그 읽기
  const ch = await page.evaluate(() => {
    const els = [...document.querySelectorAll('#v-kz .kz-card .kz-rd .kz-rk')];
    const red = els.filter(e => e.classList.contains('kz-m')), gray = els.filter(e => e.classList.contains('kz-sk'));
    return { n: els.length, nums: els.map(e => (e.querySelector('.kz-no') || {}).textContent || ''), red: red.length, gray: gray.length,
      redNums: red.map(e => e.querySelector('.kz-no').textContent).sort().join(''), redColor: red.length ? getComputedStyle(red[0].querySelector('.kz-no')).color : '',
      grayColor: gray.length ? getComputedStyle(gray[0]).color : '', btns: els.filter(e => e.tagName === 'BUTTON').map(e => e.dataset.r) };
  });
  const repN = await page.evaluate(c => __t.KC[c].rep.length, c0);
  ok(ch.n > 0 && ch.nums.every(x => /^[①-⑫]$/.test(x)) && ch.red === repN && ch.red + ch.gray === ch.n && ch.redNums === '①②③'.slice(0, repN) && /^rgb\((19[0-9]|2\d\d), /.test(ch.redColor),
    `${tag} chips ${ch.nums.join('')}: red(외울 것) ${ch.red} = 대표 소리 ${repN}개, gray ${ch.gray}`);
  if (ch.btns.length) {
    const r = ch.btns[ch.btns.length - 1];
    await page.locator(`#v-kz .kz-card .kz-rk[data-r="${r}"]`).first().tap(); await page.waitForTimeout(500);
    const c1 = await page.evaluate(r => ({ src: __t.AUD.el ? __t.AUD.el.src : '', url: __t.kzAUrl(__t.kzRdKey(r)) }), r);
    ok(c1.src === c1.url || c1.src.startsWith('blob:'), `${tag} tap reading chip ${r} → that reading's sound`);
    const a1 = await page.evaluate(() => ({ rev: __t.kui.rev, c: __t.kui.c }));
    ok(a1.rev === true && a1.c === c0, `${tag} tapping a chip keeps the card (no answer/next)`);
  }
  // [발음] 버튼
  await page.evaluate(() => { __t.AUD.stop(); if (__t.AUD.el) { __t.AUD.el.removeAttribute('src'); __t.AUD.el.load(); } });
  await page.locator('#v-kz [data-act="kzSay"].ab >> visible=true').tap(); await page.waitForTimeout(400);
  ok(await page.evaluate(c => { const s = __t.AUD.el ? __t.AUD.el.src : ''; return s === __t.kzAUrl(__t.kzRepKey(c)) || s.startsWith('blob:'); }, c0), `${tag} [발음] → representative sound again`);
  // 다음 카드로 → 소리 멈춤, 새 한자 대표 소리 미리 받아 둠
  await page.locator('#v-kz [data-act="kzOk"] >> visible=true').tap(); await page.waitForTimeout(600);
  const n1 = await page.evaluate(() => { const c = __t.kui.c, u = __t.kzAUrl(__t.kzRepKey(c)); const e = __t.AMEM.m.get(u); return { c, warm: !!e, paused: !__t.AUD.el || __t.AUD.el.paused }; });
  ok(n1.c !== c0 && n1.warm && n1.paused, `${tag} next kanji ${n1.c}: previous sound stopped, its sound prefetched`);
  await page.locator('#v-kz [data-act="kzExit"] >> visible=true').tap(); await page.waitForTimeout(300);
  // 단어 카드에서 연 한자 카드: 칩 누르면 소리
  const wid = await page.evaluate(() => { const D = JSON.parse(document.getElementById('bjt-data').textContent); return D.words.find(w => w.w === '意見').id; });
  await page.evaluate(id => { const b = document.createElement('button'); b.dataset.act = 'open'; b.dataset.id = id; document.body.appendChild(b); b.click(); b.remove(); }, wid);
  await page.waitForSelector('#sheet:not([hidden]) .s-story');
  await page.locator('#sheet-body .s-story .lk-big[data-c="見"]').tap(); await page.waitForTimeout(400);
  const sh = await page.evaluate(() => ({ t: document.getElementById('sheet-title').textContent, chips: [...document.querySelectorAll('#sheet-body .kz-rd .kz-rk')].map(e => (e.querySelector('.kz-no') || {}).textContent + e.textContent.replace(/^[①-⑫]/, '')).join(' ') }));
  ok(sh.t.includes('見') && sh.chips.startsWith('②けん') && sh.chips.includes('①みる'), `${tag} 見 card from a word card: ${sh.chips}`);
  await page.locator('#sheet-body .kz-rk[data-r="けん"]').tap(); await page.waitForTimeout(400);
  ok(await page.evaluate(() => { const s = __t.AUD.el ? __t.AUD.el.src : ''; return s === __t.kzAUrl(__t.kzRdKey('けん')) || s.startsWith('blob:'); }), `${tag} tap けん in the sheet → けん`);
  ok(await page.evaluate(() => !document.getElementById('sheet').hidden), `${tag} sheet stays open after tapping a chip`);
  // 음성 전체 받아두기 목록에 한자 소리
  const au = await page.evaluate(() => { const D = JSON.parse(document.getElementById('bjt-data').textContent); return Object.keys(D.av).filter(k => /^kr?\//.test(k)).length; });
  ok(au === dv.k + dv.kr, `${tag} kanji sounds in the audio version map: ${au}`);
  ok(errs.length === 0, `${tag} no console errors: ` + errs.join(' | '));
  await ctx.close();
}
await browser.close();
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
