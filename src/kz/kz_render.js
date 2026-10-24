/* 한자 카드 그리기 (샘플 3 틀) — 앱과 미리보기가 같이 씀. 카드 자료는 kzc.py compile 결과 */
const KZ_EMO = '"Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",sans-serif';
const KZ_INK = '#1A2133';
const kzE = s => String(s == null ? '' : s).replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
/* 글 꾸밈: **굵게**, 가나 덩어리는 일본어 글씨로 */
function kzMark(s) {
  return kzE(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/([ぁ-ゖァ-ヺー〜・]+)/g, '<span lang="ja">$1</span>');
}
function kzStrokes(card, idx, cols, vb, sw) {
  const sz = vb[2], w = sw || (3.2 * sz / 109 * 1.6);
  let p = '';
  for (let j = 0; j < idx.length; j++) p += '<path d="' + card.S[idx[j]] + '" stroke="' + (Array.isArray(cols) ? cols[j] : cols) + '"/>';
  return '<g fill="none" stroke-width="' + w.toFixed(2) + '" stroke-linecap="round" stroke-linejoin="round">' + p + '</g>';
}
function kzBox(card, idx, cols, vb, cls) {
  return '<svg viewBox="' + vb[0] + ' ' + vb[1] + ' ' + vb[2] + ' ' + vb[2] + '"' + (cls ? ' class="' + cls + '"' : '') + ' aria-hidden="true">' + kzStrokes(card, idx, cols, vb) + '</svg>';
}
function kzItems(card, items) {
  let o = '';
  for (const it of items || []) {
    const x = it.x == null ? 50 : it.x, y = it.y == null ? 50 : it.y;
    const tf = (it.r ? 'rotate(' + it.r + ' ' + x + ' ' + y + ')' : '') + (it.flip ? ' translate(' + (2 * x) + ' 0) scale(-1 1)' : '');
    const T = tf ? ' transform="' + tf.trim() + '"' : '';
    const op = it.o != null ? ' opacity="' + it.o + '"' : '';
    if (it.e != null) o += '<text x="' + x + '" y="' + y + '" font-size="' + (it.s || 40) + '" text-anchor="middle" dominant-baseline="central" style=\'font-family:' + KZ_EMO + '\'' + T + op + '>' + kzE(it.e) + '</text>';
    else if (it.t != null) o += '<text x="' + x + '" y="' + y + '" font-size="' + (it.s || 12) + '" text-anchor="middle" dominant-baseline="central" fill="' + (it.c || KZ_INK) + '" font-weight="' + (it.w || 800) + '" class="kz-stt"' + T + op + '>' + kzE(it.t) + '</text>';
    else if (it.plus) o += '<text x="' + it.plus[0] + '" y="' + it.plus[1] + '" font-size="16" text-anchor="middle" dominant-baseline="central" fill="#7A8296" class="kz-stt">+</text>';
    else if (it.arrow) {
      const [x1, y1, x2, y2] = it.arrow, a = Math.atan2(y2 - y1, x2 - x1), h = 5;
      const p1 = [x2 - h * Math.cos(a - .5), y2 - h * Math.sin(a - .5)], p2 = [x2 - h * Math.cos(a + .5), y2 - h * Math.sin(a + .5)];
      o += '<path d="M' + x1 + ' ' + y1 + ' L' + x2 + ' ' + y2 + ' M' + p1[0].toFixed(1) + ' ' + p1[1].toFixed(1) + ' L' + x2 + ' ' + y2 + ' L' + p2[0].toFixed(1) + ' ' + p2[1].toFixed(1) + '" fill="none" stroke="' + (it.c || '#7A8296') + '" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>';
    } else if (it.knife) {
      const [kx, ky, ks, kr] = it.knife;
      o += '<g transform="translate(' + kx + ' ' + ky + ') rotate(' + (kr || 0) + ') scale(' + (ks || 1) + ')"><path d="M0 0 L-5 -22 L5 -22 Z" fill="#C9D1DC" stroke="#5A6478" stroke-width="1.2" stroke-linejoin="round"/><rect x="-6.5" y="-25" width="13" height="3.2" rx="1" fill="#5A6478"/><rect x="-3" y="-38" width="6" height="13" rx="2" fill="#8A5A2B"/></g>';
    } else if (it.rect) o += '<rect x="' + it.rect[0] + '" y="' + it.rect[1] + '" width="' + it.rect[2] + '" height="' + it.rect[3] + '" rx="' + (it.rx || 0) + '" fill="' + (it.fill || 'none') + '" stroke="' + (it.stroke || 'none') + '" stroke-width="' + (it.sw || 2) + '"' + T + op + '/>';
    else if (it.circle) o += '<circle cx="' + it.circle[0] + '" cy="' + it.circle[1] + '" r="' + it.circle[2] + '" fill="' + (it.fill || 'none') + '" stroke="' + (it.stroke || 'none') + '" stroke-width="' + (it.sw || 2) + '"' + op + '/>';
    else if (it.line) o += '<line x1="' + it.line[0] + '" y1="' + it.line[1] + '" x2="' + it.line[2] + '" y2="' + it.line[3] + '" stroke="' + (it.stroke || KZ_INK) + '" stroke-width="' + (it.sw || 2) + '" stroke-linecap="round"' + op + '/>';
    else if (it.path) o += '<path d="' + kzE(it.path) + '" fill="' + (it.fill || 'none') + '" stroke="' + (it.stroke || KZ_INK) + '" stroke-width="' + (it.sw || 2) + '" stroke-linecap="round" stroke-linejoin="round"' + T + op + '/>';
    else if (it.s_) {
      const vb = it.vb, w = it.w || 60;
      o += '<svg x="' + (x - w / 2) + '" y="' + (y - w / 2) + '" width="' + w + '" height="' + w + '" viewBox="' + vb[0] + ' ' + vb[1] + ' ' + vb[2] + ' ' + vb[2] + '"' + op + '>' + kzStrokes(card, it.s_, it.cs, vb, it.sw || (vb[2] === 109 ? 6 : null)) + '</svg>';
    }
  }
  return o;
}
function kzPanel(card, p) {
  let pic;
  if (p.kc) {
    pic = '<svg viewBox="0 0 109 109" class="kz-scn" aria-hidden="true">' + (p.un ? '<g transform="scale(1.09)">' + kzItems(card, p.un) + '</g>' : '') +
      kzStrokes(card, card.S.map((_, i) => i), p.kc, [0, 0, 109], 6) + '</svg>';
  } else pic = '<svg viewBox="0 0 100 100" class="kz-scn" aria-hidden="true">' + kzItems(card, p.sc) + '</svg>';
  return '<figure class="kz-pn"><div class="kz-pic">' + pic + '</div><figcaption>' + kzMark(p.cap) + '</figcaption></figure>';
}
function kzOkuri(x) {
  const m = /^([^(]+)\(([^)]+)\)$/.exec(x);
  return m ? kzE(m[1]) + '<span class="kz-ok">' + kzE(m[2]) + '</span>' : kzE(x);
}
/* 읽기 칩(10/21): ①②③ = BJT 중요 순. 빨간 숫자·진한 칩 = 이 한자로 외울 읽기(앞면 대표 소리도 이것만), 회색 칩 = 넘어가도 되는 읽기(나오는 단어에서 익힘).
   소리 낼 수 있는 읽기는 누르면 그 읽기 발음(앱: data-act kzRd) */
const KZ_CIRC = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫';
function kzChip(x, rank, skim, isKun) {
  const plain = String(x).replace(/[()（）]/g, '');
  const say = !/っ$/.test(plain);
  const cls = 'kz-rk' + (rank ? (skim ? ' kz-sk' : ' kz-m') : '');
  const no = rank ? '<i class="kz-no">' + (KZ_CIRC[rank - 1] || rank) + '</i>' : '';
  const body = isKun ? kzOkuri(x) : kzE(x);
  return say ? '<button type="button" class="' + cls + '" data-act="kzRd" data-r="' + kzE(plain) + '" lang="ja" aria-label="' + kzE(plain) + ' 발음 듣기">' + no + body + '</button>'
    : '<span class="' + cls + '" lang="ja">' + no + body + '</span>';
}
function kzHunEum(h) { const i = h.lastIndexOf(' '); return i > 0 ? [h.slice(0, i), h.slice(i + 1)] : ['', h]; }
function kzTreeHTML(card) {
  if (!card.t || !card.t.length) return '<p class="kz-basic">' + kzMark(card.bs) + '</p>';
  const no = '①②③④⑤⑥';
  return card.t.map((st, i) => {
    const pt = st.pa.map(p => '<span class="kz-pt"><span class="kz-pg">' + kzBox(card, p.s, p.c, p.vb) + '</span><span class="kz-pl">' + kzE(p.n) + '</span>' +
      (p.r ? '<span class="kz-pr" lang="ja">' + kzE(p.r) + '</span>' : '') + (p.nt ? '<span class="kz-pn2">' + kzMark(p.nt) + '</span>' : '') + '</span>').join('<b class="kz-op">+</b>');
    const re = st.re;
    const res = '<span class="kz-pt kz-res"><span class="kz-pg">' + kzBox(card, re.s, re.cs, re.vb) + '</span><span class="kz-pl">' + kzE(re.n) + '</span>' + (re.r ? '<span class="kz-pr" lang="ja">' + kzE(re.r) + '</span>' : '') + '</span>';
    return '<div class="kz-st"><span class="kz-no">' + (no[i] || (i + 1)) + '</span><div class="kz-eq">' + pt + '<b class="kz-op">=</b>' + res + '</div><p class="kz-mini">' + kzMark(st.mi) + '</p></div>';
  }).join('');
}
/* opt.words: 단어 칸 HTML(앱이 만들어 넘김) · opt.head=false 면 머리(큰 한자·읽기) 빼고 */
function kzCardHTML(card, opt) {
  opt = opt || {};
  /* 훈음이 둘인 한자(省 '살필 성 / 덜 생')는 둘 다 '훈 음' 모양으로 */
  const hp = String(card.h).split(/\s*\/\s*/).filter(Boolean);
  const hm = hp.map(x => { const he = kzHunEum(x); return '<span class="kz-h">' + kzE(he[0]) + '</span> <span class="kz-e">' + kzE(he[1]) + '</span>'; }).join('<span class="kz-sep"> · </span>');
  const head = opt.head === false ? '' : '<header class="kz-top"><div class="kz-big" lang="ja"><span>' + kzE(card.c) + '</span></div>' +
    '<div><div class="kz-hm' + (hp.length > 1 ? ' kz-two' : '') + '">' + hm + '</div>' +
    '<div class="kz-rd"><span class="kz-lb">음독</span>' + (card.on.length ? card.on.map((x, i) => kzChip(x, card.onr && card.onr[i], card.ons && card.ons[i], false)).join('') : '<span class="kz-rk0">—</span>') + '</div>' +
    '<div class="kz-rd"><span class="kz-lb">훈독</span>' + (card.kun.length ? card.kun.map((x, i) => kzChip(x, card.kunr && card.kunr[i], card.kuns && card.kuns[i], true)).join('') : '<span class="kz-rk0">—</span>') + '</div></div></header>';
  return '<article class="kz-card">' + head +
    '<p class="kz-hook"><span class="kz-hk">' + kzE(card.h) + ' ▸</span> ' + kzMark(card.hook) + (card.br ? '<small>' + kzMark(card.br) + '</small>' : '') + '</p>' +
    '<div class="kz-strip">' + card.p.map(p => kzPanel(card, p)).join('<i class="kz-arr">→</i>') + '</div>' +
    '<section class="kz-tree"><h3>부수로 쪼개 보기 <small>작은 것부터</small></h3>' + kzTreeHTML(card) + '<p class="kz-snd">🔊 ' + kzMark(card.snd) + '</p></section>' +
    (opt.words || '') + '</article>';
}
if (typeof module !== 'undefined') module.exports = { kzCardHTML, kzMark };
