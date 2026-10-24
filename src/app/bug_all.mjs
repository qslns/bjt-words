// 10/17 버그 점검: 단어 카드 전부 · 한자 카드 전부를 실제 시트로 열어 오류·넘침·빈 칸·대체 카드 확인
import { chromium } from 'playwright';
const URL = process.env.URL || 'http://127.0.0.1:8766/';
const VPS = (process.env.VPS || '820x1180').split(',').map(s => { const [w, h] = s.split('x').map(Number); return { width: w, height: h }; });
const PART = process.env.PART || 'wk';
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const out = {};
for (const vp of VPS) {
  const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: 1, serviceWorkers: 'block', hasTouch: true });
  const page = await ctx.newPage(); const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource|fonts\.g/.test(m.text())) errs.push(m.text()); });
  await page.goto(URL + '?t=' + Date.now());
  await page.waitForSelector('#v-home details.gf', { state: 'attached', timeout: 60000 });
  const tag = vp.width + 'x' + vp.height;
  // 1) 문자열 수준: 한자 카드 950장이 그림 카드로 그려지는지(대체 카드로 떨어지지 않는지), 단원 앞면
  if (PART.includes('k')) {
    out[tag + ':kzStr'] = await page.evaluate(() => {
      const t = window.__t, bad = [];
      for (const c of t.KZO) {
        const card = t.KC[c];
        if (!card) { bad.push(c + ':no card'); continue; }
        let h = '';
        try { h = kzCardHTML(card, { words: '' }); } catch (e) { bad.push(c + ':throw ' + e.message); continue; }
        if (/undefined|NaN|\[object/.test(h)) bad.push(c + ':undef/NaN');
        const b = t.kzBodyHTML(c);
        if (!b.includes('kz-strip')) bad.push(c + ':fallback');
        if (!b.includes('kzu-ws')) bad.push(c + ':no words');
      }
      return { n: t.KZO.length, bad };
    });
  }
  // 2) 한자 카드 시트를 실제로 열기(전부)
  if (PART.includes('k')) {
    const kz = await page.evaluate(() => window.__t.KZO);
    const bad = []; let worst = 0, at = '';
    for (const c of kz) {
      await page.evaluate(c => { const b = document.createElement('button'); b.dataset.act = 'kz'; b.dataset.c = c; document.body.appendChild(b); b.click(); b.remove(); }, c);
      const r = await page.evaluate(c => {
        const sb = document.getElementById('sheet-body'), sh = document.getElementById('sheet');
        if (!sh || sh.hidden) return { e: 'sheet hidden' };
        const card = sb.querySelector('.kz-card');
        const title = document.getElementById('sheet-title').textContent;
        const html = sb.innerHTML;
        const ids = [...sb.querySelectorAll('.kzu-ws .sk-w')].map(b => +b.dataset.id);
        const pics = sb.querySelectorAll('.kz-strip .kz-pn').length;
        const over = Math.max(document.documentElement.scrollWidth - innerWidth, sb.scrollWidth - sb.clientWidth);
        // 그림 칸 안 글자가 그림 밖으로 나가는지(svg bbox)
        let clip = 0;
        sb.querySelectorAll('.kz-pic > svg').forEach(svg => { try { const vb = svg.viewBox.baseVal, bb = svg.getBBox(); const m = Math.max(vb.x - bb.x, vb.y - bb.y, bb.x + bb.width - (vb.x + vb.width), bb.y + bb.height - (vb.y + vb.height)); if (m > clip) clip = m; } catch (e) {} });
        return { card: !!card, title, undef: /undefined|NaN|\[object/.test(html), ids, pics, over, clip, hasC: title.includes(c) };
      }, c);
      if (r.e) bad.push(c + ':' + r.e);
      else {
        if (!r.card) bad.push(c + ':no card');
        if (!r.hasC) bad.push(c + ':title ' + r.title);
        if (r.undef) bad.push(c + ':undef');
        if (!r.ids.length) bad.push(c + ':no words');
        if (r.ids.some(x => !Number.isFinite(x))) bad.push(c + ':bad id');
        if (r.pics !== 3) bad.push(c + ':pics ' + r.pics);
        if (r.over > worst) { worst = r.over; at = c; }
        if (r.clip > 12) bad.push(c + ':clip ' + Math.round(r.clip));
      }
      await page.evaluate(() => { const b = document.querySelector('#sheet .sheet-head [data-act="closeSheet"]'); if (b) b.click(); });
    }
    out[tag + ':kzSheets'] = { n: kz.length, worstOverflow: worst, at, bad: bad.slice(0, 60), nbad: bad.length };
  }
  // 3) 단어 카드 시트를 실제로 열기(전부)
  if (PART.includes('w')) {
    const ids = await page.evaluate(() => { const D = JSON.parse(document.getElementById('bjt-data').textContent); return D.words.map(w => w.id); });
    const bad = []; let worst = 0, at = '';
    for (const id of ids) {
      await page.evaluate(id => { const b = document.createElement('button'); b.dataset.act = 'open'; b.dataset.id = id; document.body.appendChild(b); b.click(); b.remove(); }, id);
      const r = await page.evaluate(() => {
        const sb = document.getElementById('sheet-body'), sh = document.getElementById('sheet');
        if (!sh || sh.hidden) return { e: 'sheet hidden' };
        const html = sb.innerHTML;
        const over = Math.max(document.documentElement.scrollWidth - innerWidth, sb.scrollWidth - sb.clientWidth);
        const kbtn = [...sb.querySelectorAll('[data-act="kz"]')].map(b => b.dataset.c);
        return { undef: /undefined|NaN|\[object/.test(html), over, kbtn, ex: !!sb.querySelector('.ex'), sents: sb.querySelectorAll('.ex-b .sent, .ex-b [data-act="say"], .ex-b li').length };
      });
      if (r.e) bad.push(id + ':' + r.e);
      else {
        if (r.undef) bad.push(id + ':undef');
        if (!r.ex) bad.push(id + ':no ex');
        if (r.over > worst) { worst = r.over; at = id; }
        const noCard = await page.evaluate(cs => cs.filter(c => !window.__t.KC[c]), r.kbtn);
        if (noCard.length) bad.push(id + ':kz btn w/o card ' + noCard.join(''));
      }
      await page.evaluate(() => { const b = document.querySelector('#sheet .sheet-head [data-act="closeSheet"]'); if (b) b.click(); });
    }
    out[tag + ':wordSheets'] = { n: ids.length, worstOverflow: worst, at, bad: bad.slice(0, 60), nbad: bad.length };
  }
  out[tag + ':errs'] = errs.slice(0, 20);
  await ctx.close();
}
console.log(JSON.stringify(out, null, 1));
await browser.close();
