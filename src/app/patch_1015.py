# ================= 10/15: 홈 큰 묶음(0부 기본 1·2, 1–3부) 기본으로 접기 =================
# (한자 암기 단원·단어 카드 한자칸 그림 연상은 사용자 요청으로 10/15 철회 — patch_1015.py.kanji_bak 참고)
# patch_app.py 맨 끝(쓰기 직전)에서 exec 로 실행됨 — rep()/s 를 그대로 씀

CSS_1015 = r'''
/* ---------- 10/15: 홈 묶음 접기 ---------- */
.gf{border:1px solid var(--line);border-radius:12px;background:var(--surface)}
.gf>summary{list-style:none;cursor:pointer;min-height:56px;padding:10px 16px;display:flex;align-items:center;gap:6px 12px;flex-wrap:wrap;-webkit-user-select:none;user-select:none}
.gf>summary::-webkit-details-marker{display:none}
.gf>summary b{font-size:17px}
.gf .g-p{font-size:13px;color:var(--ink-3)}
.gf .g-on{font-size:12px;font-weight:700;color:var(--stamp);border:1px solid var(--stamp);border-radius:999px;padding:1px 8px}
.gf .fold{font-size:13px;color:var(--ink-3);white-space:nowrap}
.gf .fold::after{content:"펼치기 +"}
.gf[open] .fold::after{content:"접기 −"}
.gf>.g-in{padding:2px 14px 16px;display:flex;flex-direction:column;gap:10px}
'''
rep('</style>\n</head>', CSS_1015 + '</style>\n</head>')

# ---------- 홈: 큰 묶음은 접어 두기 ----------
rep("""  return parts.map((ps, p) => {
    const a = p * 500 + 1, b = Math.min(BTOTAL, a + 499);
    return '<section class="grp grp-basic"><div class="grp-h"><b>0부 · 기본' + (parts.length > 1 ? ' ' + (p + 1) : '') + '</b><span>기본 ' + a + '–' + b + '</span><i class="rule"></i></div>' +
      (p === 0 ? '<p class="part-h">N5·N4 단어 중 BJT에 나오는 기초 단어 · 1500 단어와 겹치는 건 같은 카드 · 250개씩 50개 단위로 쌓아 가며 회독</p>' : '') +
      '<div class="books">' + ps.map(c => bookHTML(c)).join('') + '</div></section>';
  }).join('')""",
    """  return parts.map((ps, p) => {
    const a = p * 500 + 1, b = Math.min(BTOTAL, a + 499);
    return foldHTML('b' + p, 'grp-basic', '0부 · 기본' + (parts.length > 1 ? ' ' + (p + 1) : ''), '기본 ' + a + '–' + b, ps,
      (p === 0 ? '<p class="part-h">N5·N4 단어 중 BJT에 나오는 기초 단어 · 1500 단어와 겹치는 건 같은 카드 · 250개씩 50개 단위로 쌓아 가며 회독</p>' : '') +
      '<div class="books">' + ps.map(c => bookHTML(c)).join('') + '</div>');
  }).join('')""")
rep("""  let out = parts.map((cs, p) => {
    const a = p * 500 + 1, b = Math.min(TOTAL, a + 499);
    return '<section class="grp"><div class="grp-h"><b>' + (p + 1) + '부 · ' + (lab[p] || '보충') + '</b><span>No.' + a + '–' + b + '</span><i class="rule"></i></div>' +
      '<p class="part-h">250개씩 50개 단위로 쌓아 가며 회독 → 마지막 장은 ' + a + '–' + b + ' 총정리</p>' +
      '<div class="books">' + cs.map(c => bookHTML(c)).join('') + '</div></section>';
  }).join('');""",
    """  let out = parts.map((cs, p) => {
    const a = p * 500 + 1, b = Math.min(TOTAL, a + 499);
    return foldHTML('p' + p, '', (p + 1) + '부 · ' + (lab[p] || '보충'), 'No.' + a + '–' + b, cs,
      '<p class="part-h">250개씩 50개 단위로 쌓아 가며 회독 → 마지막 장은 ' + a + '–' + b + ' 총정리</p>' +
      '<div class="books">' + cs.map(c => bookHTML(c)).join('') + '</div>');
  }).join('');""")
FOLD_JS = r'''/* 홈의 큰 묶음(0부·1부…)은 접어 두고 눌러서 펼침. 펼친 묶음은 앱을 쓰는 동안 기억(홈을 다시 그려도 유지) */
const GOPEN = new Set();
document.addEventListener('toggle', e => { const d = e.target; if (d && d.matches && d.matches('details.gf[data-g]')) { if (d.open) GOPEN.add(d.dataset.g); else GOPEN.delete(d.dataset.g); } }, true);
function foldHTML(key, cls, title, range, cs, inner) {
  const done = cs.filter(c => H.ch[c.i] && H.ch[c.i].n > 0).length, on = cs.some(c => H.ch[c.i] && H.ch[c.i].cur);
  return '<section class="grp' + (cls ? ' ' + cls : '') + '"><details class="gf" data-g="' + key + '"' + (GOPEN.has(key) ? ' open' : '') + '>' +
    '<summary class="grp-h"><b>' + title + '</b><span>' + range + '</span><span class="g-p">끝낸 장 ' + done + '/' + cs.length + '</span>' + (on ? '<span class="g-on">진행중</span>' : '') + '<i class="rule"></i><span class="fold"></span></summary>' +
    '<div class="g-in">' + inner + '</div></details></section>';
}
function basicHTML() {'''
rep("function basicHTML() {", FOLD_JS)

# ---------- 단어 카드 한자칸: 음(음독)도 히라가나로 (사용자: 가타카나 잘 못 읽음) ----------
rep("'<div class=\"kv\"><span class=\"lb\">음</span><span lang=\"ja\">' + (k.on.length ? esc(k.on.join('・')) : '—') + '</span></div>' +",
    "'<div class=\"kv\"><span class=\"lb\">음</span><span lang=\"ja\">' + (k.on.length ? esc(k.on.map(toHira).join('・')) : '—') + '</span></div>' +")
