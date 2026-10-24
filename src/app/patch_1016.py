# ================= 10/16: 단어 카드 한자칸 · 한자 카드 시트 · 한자 단원 =================
# patch_app.py 맨 끝(patch_1015b.py 다음, 쓰기 직전)에서 exec 로 실행됨 — rep()/s 를 그대로 씀
# - 단어 카드: '이야기' 칸 → '한자' 칸(훈음 + 이 단어 읽기 / 카드 장면 한 줄), '한자·부수 풀이' 접는 칸 없앰, 설정의 '한자 풀이 접기/펼치기' 없앰
# - 네모 한자(한자칸·같은 한자 칸) 누르면 한자 카드 시트(단어 카드 시트와 같은 쌓기·뒤로가기)
# - 홈 '한자' 묶음 + 한자 단원(단어 공부와 같은 화면·흐름, 기록은 'bjt500.kanji.v1'에 따로)
# 한자 카드 모양(kz/kz.css)·그리는 함수(kz/kz_render.js)는 미리보기(preview.py)와 같은 파일을 빌드 때 그대로 읽어 넣음(복사본 없음)

KZ_DIR = '/home/claude/work/kz'
KZ_CSS_SRC = open(KZ_DIR + '/kz.css', encoding='utf-8').read()
KZ_JS_SRC = open(KZ_DIR + '/kz_render.js', encoding='utf-8').read()
if '</style' in KZ_CSS_SRC.lower() or '</script' in KZ_JS_SRC.lower() or '<!--' in KZ_JS_SRC:
    raise SystemExit('kz.css / kz_render.js: closing tag inside — cannot inline')

CSS_1016 = r'''
/* ---------- 10/16: 한자칸 · 한자 카드 · 한자 단원 ---------- */
/* 단어 카드 한자칸·같은 한자 칸의 네모 한자 = 한자 카드 버튼 */
button.lk-big,button.sk-k{color:var(--ink);padding:0;-webkit-tap-highlight-color:transparent}
button.lk-big:active,button.sk-k:active{background:var(--surface-2)}
.lk-hs .lk-r{margin-left:8px;font-size:13px;font-weight:400;color:var(--ink-2);font-family:var(--f-jp)}
/* 한자 카드 맨 아래 단어 목록(같은 한자 칸 단어 모양) */
.kzu-ws .sec-h{margin-bottom:8px}
.kzu-ws .sk-j{white-space:normal;overflow-wrap:anywhere}
.kzu-ws .sk-w.long .sk-j{font-size:24px}
/* 한자 단원: 공부 화면은 단어 공부 화면과 같은 틀(아래 버튼 자리 고정도 같게) */
#v-kz .abar-in{display:grid;grid-template-columns:repeat(3,minmax(0,360px));justify-content:center}
#v-kz .ab{max-width:none;min-width:0}
#v-kz .ab-next{grid-column:span 2;max-width:none}
#v-kz .kz-card{width:100%;max-width:980px;margin:6px auto 0}
.kzu-ph{font-size:13px;font-weight:600;color:var(--ink-2);margin-top:4px}
/* 다크 모드: 카드 안 회색 글씨만 앱 회색으로(밝은 바탕 칸은 카드 색 그대로) */
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .kz-card{--kz-ink2:var(--ink-2);--kz-ink3:var(--ink-3)}}
:root[data-theme="dark"] .kz-card{--kz-ink2:var(--ink-2);--kz-ink3:var(--ink-3)}
'''
rep('</style>\n</head>', '\n/* ---------- 한자 카드 모양: kz/kz.css (빌드 때 그대로 읽어 넣음) ---------- */\n' + KZ_CSS_SRC + CSS_1016 + '</style>\n</head>')

# ---------- 화면 자리 · 한자 카드 그리기 스크립트(따로 둠: 이 스크립트가 잘못돼도 단어 공부 스크립트는 그대로 돎) ----------
rep('  <section class="view" id="v-light" hidden></section>\n',
    '  <section class="view" id="v-light" hidden></section>\n  <section class="view" id="v-kz" hidden></section>\n')
rep('<script type="application/json" id="bjt-data">__BJT_DATA__</script>\n<script>\n',
    '<script type="application/json" id="bjt-data">__BJT_DATA__</script>\n<script>\n/* 한자 카드 그리기: kz/kz_render.js (빌드 때 그대로 읽어 넣음) */\n' + KZ_JS_SRC.rstrip() + '\n</script>\n<script>\n')

# ---------- 단어 카드: '이야기' 칸 → '한자' 칸 ----------
rep("""/* 이야기: 부수 → 한자 → 단어 (처음 보는 사람이 바로 이해하도록) */
function storyHTML(w, cls) {
  const ks = [...new Set(w.kj || [])].filter(c => K[c]);
  const rows = ks.map(c => {
    const k = K[c];
    const h = k.h && k.h.charAt(0) !== '?' ? k.h : (k.h ? k.h.replace(/^\\?\\s*/, '') : '');
    return '<div class="lk"><span class="lk-big" lang="ja">' + esc(c) + '</span><div class="lk-t">' +
      '<span class="lk-hs">' + (h ? '<b>' + esc(h) + '</b>' : '') + (k.s ? (h ? ' · ' : '') + mixJa(k.s) : '') + '</span>' +
      (k.x ? '<p class="lk-x">' + emArrow(k.x, true) + '</p>' : '') + '</div></div>';
  }).join('');
  const st = w.st ? '<p class="st-w">' + emArrow(w.st, false) + '</p>' : '';
  if (!rows && !st) return '';
  return '<section class="' + cls + ' story"><span class="sl">이야기</span>' + rows + st + '</section>';
}""",
"""/* 한자칸(10/16, 옛 '이야기'): 한자마다 [네모 한자 = 한자 카드 버튼] 훈음 + 이 단어에서의 읽기 / 카드의 장면 한 줄(hook).
   카드가 없는 한자는 옛 '구성 + 풀이' 그대로. 단어 전체 이야기 줄(단어 → …)은 그대로. 한자가 없는 단어(가나·가타카나)는 칸 이름 '이야기' 그대로 */
function storyHTML(w, cls) {
  const ks = [...new Set(w.kj || [])].filter(c => K[c]);
  const krm = {};
  (w.kr || []).forEach(p => { if (p && p[0] && p[1]) (krm[p[0]] = krm[p[0]] || []).push(toHira(p[1])); });
  const rows = ks.map(c => {
    const k = K[c], card = KC[c];
    const h = k.h && k.h.charAt(0) !== '?' ? k.h : (k.h ? k.h.replace(/^\\?\\s*/, '') : '');
    const big = '<button class="lk-big" data-act="kz" data-c="' + esc(c) + '" lang="ja" aria-label="' + esc(c) + ' 한자 카드 보기">' + esc(c) + '</button>';
    if (card && card.hook) {
      const rd = krm[c] ? [...new Set(krm[c])].join('・') : '';
      return '<div class="lk">' + big + '<div class="lk-t">' +
        '<span class="lk-hs">' + (h ? '<b>' + esc(h) + '</b>' : '') + (rd ? '<small class="lk-r" lang="ja">' + esc(rd) + '</small>' : '') + '</span>' +
        '<p class="lk-x lk-hook">' + kzHook(card) + '</p></div></div>';
    }
    return '<div class="lk">' + big + '<div class="lk-t">' +
      '<span class="lk-hs">' + (h ? '<b>' + esc(h) + '</b>' : '') + (k.s ? (h ? ' · ' : '') + mixJa(k.s) : '') + '</span>' +
      (k.x ? '<p class="lk-x">' + emArrow(k.x, true) + '</p>' : '') + '</div></div>';
  }).join('');
  const st = w.st ? '<p class="st-w">' + emArrow(w.st, false) + '</p>' : '';
  if (!rows && !st) return '';
  return '<section class="' + cls + ' story"><span class="sl">' + (rows ? '한자' : '이야기') + '</span>' + rows + st + '</section>';
}""")

# ---------- 단어 카드: '한자·부수 풀이' 접는 칸 없앰(해설 화면·시트 둘 다 explainHTML) ----------
rep(" : -1) + kpHTML(w) + '</div></div>';", " : -1) + '</div></div>';")
# 설정: '한자 풀이 접어 두기/펼쳐 두기' 없앰 — 저장된 S.kp 값은 그대로 둬도 아무 데도 안 씀(오류 없음)
rep(" + segB('setKp', S.kp, [[false, '한자 풀이 접어 두기'], [true, '한자 풀이 펼쳐 두기']])", "")

# ---------- 같은 한자 칸: 네모 한자 = 한자 카드 버튼 ----------
rep("""<span class="sk-kc"><span class="sk-k" lang="ja">' + esc(c) + '</span>'""",
    """<span class="sk-kc"><button class="sk-k" data-act="kz" data-c="' + esc(c) + '" lang="ja" aria-label="' + esc(c) + ' 한자 카드 보기">' + esc(c) + '</button>'""")

# ---------- 시트: 한자 카드(t:'kz') · 한자 장 목록(t:'kzl') — 단어 카드와 같은 쌓기·뒤로가기 ----------
rep("  if (en.t === 'ch') renderChList(en.i);\n",
    "  if (en.t === 'ch') renderChList(en.i);\n"
    "  else if (en.t === 'kz' || en.t === 'kzl') { if (!(en.t === 'kz' ? kzSheet(en.c) : kzListSheet(en.i))) closeSheet(); }\n")

# ---------- 동작: 'kz…' 은 한자 쪽에서 처리(기존 동작 이름과 안 겹침) ----------
rep("function act(a, el) {\n  const idAttr = el.dataset.id != null ? +el.dataset.id : null;\n",
    "function act(a, el) {\n  const idAttr = el.dataset.id != null ? +el.dataset.id : null;\n"
    "  if (a.slice(0, 2) === 'kz') { kzAct(a, el); return; }\n")

# ---------- 홈: '한자' 접는 묶음(1–3부 다음, 단어 목록 줄 위) ----------
rep("basicHTML() + partsHTML() +\n", "basicHTML() + partsHTML() + kzHomeHTML() +\n")
# foldHTML: 끝낸 장·진행중을 밖에서 줄 수 있게(한자 기록은 H가 아니라 KZ). 단어 묶음은 예전과 똑같이 계산
rep("function foldHTML(key, cls, title, range, cs, inner) {\n"
    "  const done = cs.filter(c => H.ch[c.i] && H.ch[c.i].n > 0).length, on = cs.some(c => H.ch[c.i] && H.ch[c.i].cur);\n",
    "function foldHTML(key, cls, title, range, cs, inner, st) {\n"
    "  const done = st ? st.done : cs.filter(c => H.ch[c.i] && H.ch[c.i].n > 0).length, on = st ? st.on : cs.some(c => H.ch[c.i] && H.ch[c.i].cur);\n")
# 한자 공부 중에도 화면 꺼짐 막기
rep("  wake(v === 'study' || v === 'light');\n}", "  wake(v === 'study' || v === 'light' || v === 'kz');\n}")

# ---------- 진도 백업: 한자 단원 기록도 같이(따로 칸 kz, 예전 코드·예전 앱과 호환) ----------
rep("  const raw = new TextEncoder().encode(JSON.stringify({v: 2, h: H, s: S, at: Date.now()}));",
    "  const raw = new TextEncoder().encode(JSON.stringify(Object.assign({v: 2, h: H, s: S, at: Date.now()}, kzHas() ? {kz: KZ} : {})));")
rep("  mergeH(o.h);\n  if (o.s) mergeS(o.s);\n",
    "  mergeH(o.h);\n  if (o.s) mergeS(o.s);\n  let kzIn = false; if (o.kz) { try { kzIn = kzMerge(o.kz); } catch (e) { kzIn = false; } }\n")
rep("  toast(before === JSON.stringify(H) ? '이미 같은 진도예요' : '가져왔어요 · 단어 기록 ' + Object.keys(H.w).length + '개');",
    "  toast(before === JSON.stringify(H) && !kzIn ? '이미 같은 진도예요' : '가져왔어요 · 단어 기록 ' + Object.keys(H.w).length + '개' + (kzIn ? ' · 한자 기록 ' + Object.keys(KZ.w).length + '자' : ''));")

KZ_JS = r'''/* ================= 10/16 한자: 한자 카드 시트 · 한자 단원 =================
   카드 DATA.kc(kz/kzc.py compile) · 순서 DATA.kzo(많이 쓰는 순) · 그리기 kzCardHTML/kzMark(kz/kz_render.js, 앞의 따로 된 스크립트)
   한자 단원 기록은 단어 기록(H)과 완전히 따로(localStorage 'bjt500.kanji.v1') — 약점·단어 통계·단어 장 진도에 안 섞임 */
const KC = obj(DATA.kc);
const KZO = (() => { const out = [], seen = new Set(); for (const c of (Array.isArray(DATA.kzo) ? DATA.kzo : [])) { if (typeof c === 'string' && K[c] && !seen.has(c)) { seen.add(c); out.push(c); } } return out; })();
const KZN = KZO.length, KZNO = new Map(KZO.map((c, i) => [c, i + 1]));
const kzHs = ids => { let h = 2166136261; for (const c of ids) { h ^= c.codePointAt(0); h = Math.imul(h, 16777619) >>> 0; } return h.toString(36) + '.' + ids.length; };
/* 장: 단어와 같은 규칙(250자 안에서 50자씩 누적 → 500자마다 총정리 → 전체) */
const KZCH = genChapters(KZN).map((c, i) => { const ids = KZO.slice(c.a - 1, c.b); return Object.assign(c, {i, ids, cnt: ids.length, key: 'K:' + kzHs(ids) + ':' + c.a + '-' + c.b + ':' + c.kind}); });
const kzName = i => '漢字' + (i + 1) + '章';
const kzRange = c => c.a + '–' + c.b + '자';
const kzH = c => String((K[c] && K[c].h) || '').replace(/^\?\s*/, '').trim();
const kzHook = card => { try { if (typeof kzMark === 'function') return kzMark(card.hook); } catch (e) { /* 아래 */ } return esc(card.hook).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>'); };
const KZV = $('#v-kz'); if (KZV) V.kz = KZV;

/* ----- 기록(단어 기록과 따로) ----- */
const KZK = 'bjt500.kanji.v1';
const kzBlank = () => ({ch: {}, w: {}, g: {tt: 0, d: {}}, u: 0});
function kzCleanRun(r) {
  if (!r || typeof r !== 'object') return null;
  const ids = a => Array.isArray(a) ? a.filter(c => typeof c === 'string' && KZNO.has(c)) : [];
  const o = {ord: ids(r.ord), pos: 0, unk: ids(r.unk), ph: r.ph === 'loop' ? 'loop' : 'main', q: ids(r.q), qpos: 0, next: ids(r.next), round: nn(r.round), shuf: r.shuf !== false, t: nn(r.t), k: nn(r.k), started: nn(r.started), u: nn(r.u)};
  if (!o.ord.length) return null;
  o.pos = Math.min(Math.floor(nn(r.pos)), o.ord.length);
  o.qpos = Math.min(Math.floor(nn(r.qpos)), o.q.length);
  if (o.ph === 'loop' && !o.q.length && !o.next.length) o.qpos = 0;
  return o;
}
const kzCleanW = x => { x = obj(x); return {n: nn(x.n), m: nn(x.m), l: x.l === 1 ? 1 : x.l === 0 ? 0 : -1, t: nn(x.t), u: nn(x.u)}; };
function kzNorm(o) {
  const z = kzBlank();
  if (!o || typeof o !== 'object') return z;
  const ch = obj(o.ch);
  for (const c of KZCH) { const x = ch[c.key]; if (!x || typeof x !== 'object') continue; z.ch[c.key] = {n: nn(x.n), cur: kzCleanRun(x.cur), t: nn(x.t), last: cleanLast(x.last), u: nn(x.u)}; }
  const w = obj(o.w);
  for (const c in w) if (KZNO.has(c)) z.w[c] = kzCleanW(w[c]);
  const g = obj(o.g); z.g.tt = nn(g.tt);
  const d = obj(g.d); for (const k in d) if (/^\d{4}-\d{2}-\d{2}$/.test(k)) z.g.d[k] = nn(d[k]);
  z.u = nn(o.u);
  return z;
}
let KZ = (() => { try { return kzNorm(LS.get(KZK)); } catch (e) { return kzBlank(); } })();
function kzSave() { KZ.u = Date.now(); LS.set(KZK, KZ); }
const kzHas = () => Object.keys(KZ.ch).length > 0 || Object.keys(KZ.w).length > 0;
const kzChPeek = i => KZCH[i] ? (KZ.ch[KZCH[i].key] || null) : null;
const kzChGet = i => KZ.ch[KZCH[i].key] || (KZ.ch[KZCH[i].key] = {n: 0, cur: null, t: 0, last: null, u: 0});
const kzWGet = c => KZ.w[c] || (KZ.w[c] = {n: 0, m: 0, l: -1, t: 0, u: 0});
/* 진도 가져오기: 장·한자마다 더 최근 기록이 남음 */
function kzMerge(R) {
  const r = kzNorm(R); let ch = false;
  for (const k in r.ch) { const l = KZ.ch[k], x = r.ch[k]; if (!l || x.u > l.u) { KZ.ch[k] = x; ch = true; } }
  for (const c in r.w) { const l = KZ.w[c], x = r.w[c]; if (!l || x.u > l.u) { KZ.w[c] = x; ch = true; } }
  if (r.g.tt > KZ.g.tt) { KZ.g.tt = r.g.tt; ch = true; }
  for (const d in r.g.d) if (r.g.d[d] > (KZ.g.d[d] || 0)) { KZ.g.d[d] = r.g.d[d]; ch = true; }
  if (ch) kzSave();
  return ch;
}

/* ----- 한자 카드(시트·해설 공통): 카드 + 맨 아래 이 한자가 든 단어 전부(본편 순서 → 기본 순서) ----- */
function kzWordsHTML(c) {
  const k = K[c]; if (!k) return '';
  const ids = [...new Set(Array.isArray(k.u) ? k.u : [])].filter(id => byId.has(id)).sort((a, b) => sortNo(a) - sortNo(b));
  if (!ids.length) return '';
  return '<section class="kzu-ws"><h3 class="sec-h"><span>이 한자가 든 단어</span><i class="rule"></i><span class="aux">' + ids.length + '</span></h3><div class="sk-ws">' +
    ids.map(id => { const o = byId.get(id); return '<button class="sk-w' + ([...o.w].length >= 8 ? ' long' : '') + '" data-act="open" data-id="' + id + '"><span class="sk-j" lang="ja">' + headRuby(o) + '</span><span class="sk-m">' + mixJa(shortM(o.m)) + '</span></button>'; }).join('') +
  '</div></section>';
}
/* 카드가 없는(또는 못 그린) 한자: 큰 한자 · 훈음 · 음독/훈독(히라가나) · 옛 구성/풀이 · 단어 목록 */
function kzSimpleHTML(c, words) {
  const k = K[c] || {}, h = kzH(c), sp = h.lastIndexOf(' ');
  const on = Array.isArray(k.on) ? k.on : [], kun = Array.isArray(k.kun) ? k.kun : [];
  const okuri = x => { const m = /^([^(]+)\(([^)]+)\)$/.exec(String(x)); return m ? esc(m[1]) + '<span class="kz-ok">' + esc(m[2]) + '</span>' : esc(x); };
  const rd = (lb, xs) => '<div class="kz-rd"><span class="kz-lb">' + lb + '</span>' + (xs.length ? xs.map(x => '<span class="kz-rk" lang="ja">' + x + '</span>').join('') : '<span class="kz-rk0">—</span>') + '</div>';
  return '<article class="kz-card kz-simple"><header class="kz-top"><div class="kz-big" lang="ja"><span>' + esc(c) + '</span></div>' +
    '<div><div class="kz-hm"><span class="kz-h">' + esc(sp > 0 ? h.slice(0, sp) : '') + '</span> <span class="kz-e">' + esc(sp > 0 ? h.slice(sp + 1) : h) + '</span></div>' +
    rd('음독', on.map(x => esc(toHira(x)))) + rd('훈독', kun.map(okuri)) + '</div></header>' +
    (k.s || k.x ? '<section class="kz-tree"><h3>구성 · 풀이</h3>' + (k.s ? '<p class="kz-basic">' + mixJa(k.s) + '</p>' : '') + (k.x ? '<p class="kz-basic">' + emArrow(k.x, true) + '</p>' : '') + '</section>' : '') +
    words + '</article>';
}
function kzBodyHTML(c) {
  const words = kzWordsHTML(c), card = KC[c];
  if (card && typeof kzCardHTML === 'function') {
    try { const h = kzCardHTML(card, {words}); if (typeof h === 'string' && h && !/undefined|NaN/.test(h)) return h; } catch (e) { /* 간단한 카드로 */ }
  }
  return kzSimpleHTML(c, words);
}
function kzSheet(c) {
  if (typeof c !== 'string' || !K[c]) return false;
  const h = kzH(c);
  openSheet('<span lang="ja">' + esc(c) + '</span>' + (h ? ' · ' + esc(h) : ''), '<div class="sheet-stage"><div class="kzu-sh">' + kzBodyHTML(c) + '</div></div>');
  return true;
}
/* 단어 카드 시트와 같은 규칙: 시트 밖에서 누르면 새로, 시트 안에서 누르면 쌓기(뒤로가기로 돌아감) */
function openKz(c, inSheet) {
  if (typeof c !== 'string' || !K[c]) return;
  if (!inSheet) sheetStack = [];
  sheetStack.push({t: 'kz', c});
  sheetShow(sheetStack[sheetStack.length - 1]);
}
function kzRowHTML(c) {
  const x = KZ.w[c], st = !x || x.l === -1 ? 'new' : x.l === 1 ? 'ok' : 'ng', on = ((K[c] && K[c].on) || []).map(toHira).join('・');
  return '<li><button class="row" data-act="kz" data-c="' + esc(c) + '"><span class="num">' + KZNO.get(c) + '</span>' +
    '<span class="rw"><span class="w" lang="ja">' + esc(c) + '</span>' + (on ? '<span class="r" lang="ja">' + esc(on) + '</span>' : '') + '</span>' +
    '<span class="rm">' + esc(kzH(c)) + '</span><span class="rd">' + (x && x.m ? '<span class="miss">×' + x.m + '</span>' : '') + '<i class="dot st-' + st + '" title="' + ST_NAME[st] + '"></i></span></button></li>';
}
function kzListSheet(i) {
  const c = KZCH[i]; if (!c) return false;
  const ch = kzChPeek(i), ng = c.ids.filter(k => KZ.w[k] && KZ.w[k].l === 0).length;
  openSheet(kzName(i) + ' · ' + kzRange(c),
    '<div class="sheet-tools"><span class="note">' + c.ids.length + '자 · 모름 ' + ng + (ch && ch.n ? ' · ' + ch.n + '회 완료' : '') + '</span></div>' +
    '<ul class="list" id="kz-list">' + c.ids.map(kzRowHTML).join('') + '</ul>' +
    '<div class="danger-zone"><button class="btn danger" data-act="kzReset" data-k="' + i + '">이 장 기록 초기화</button><p class="note" style="margin-top:8px">이 장의 회독 수·진행 상태만 지워요. 한자별 기록은 그대로.</p></div>');
  return true;
}

/* ----- 홈: '한자' 묶음 ----- */
function kzBookHTML(c) {
  const ch = kzChPeek(c.i) || {n: 0, cur: null, last: null};
  const inprog = !!ch.cur;
  const last = ch.last ? '지난번 ' + pct(ch.last.k, ch.last.tot) + '% 알고있음' : '';
  return '<div class="book kzu-book blk' + c.blk + '" data-act="kzOpen" data-k="' + c.i + '" role="button" tabindex="0" aria-label="' + kzName(c.i) + ' ' + (ch.n + 1) + '회독 ' + kzRange(c) + '">' +
    '<i class="spine"></i>' + (inprog ? '<span class="ribbon">진행중</span>' : '') +
    '<div class="bbody"><b class="b-ch" lang="ja">' + kzName(c.i) + '</b>' +
      '<span class="b-range">' + kzRange(c) + '</span>' +
      '<span class="b-pass">' + (ch.n + 1) + '회독 · ' + c.cnt + '자</span>' +
      (inprog ? '<span class="b-sub">진행 ' + progText(ch.cur) + '</span>' : '') +
      (ch.n ? '<span class="b-done">' + ch.n + '회 완료' + (last ? ' · ' + last : '') + '</span>' : '') +
    '</div>' +
    '<div class="b-acts"><button class="b-btn" data-act="kzList" data-k="' + c.i + '" aria-label="' + kzName(c.i) + ' 한자 목록">' + ICON.list + '</button>' +
      (inprog ? '<button class="b-btn" data-act="kzRestart" data-k="' + c.i + '" aria-label="' + kzName(c.i) + ' 처음부터 다시">' + ICON.restart + '</button>' : '') + '</div>' +
  '</div>';
}
function kzUnitOn() { try { return localStorage.getItem('bjt500.kzunit') !== '0'; } catch (e) { return true; } }   /* 10/17 검수 끝 → 공개 */
function kzHomeHTML() {
  if (!KZN || !V.kz || !kzUnitOn()) return '';   /* 한자 단원은 토요일 검수 뒤 공개(시험은 bjt500.kzunit=1로 켬) */
  try {
    const parts = [];
    KZCH.forEach(c => { if (c.kind !== 'all') (parts[c.part] = parts[c.part] || []).push(c); });
    const all = KZCH.find(c => c.kind === 'all');
    const inner = '<p class="part-h">단어에 나오는 한자 ' + KZN + '자 · 많이 쓰는 순 · 250자 안에서 50자씩 쌓아 가며 회독 · 기록은 단어와 따로</p>' +
      parts.map((ps, p) => (parts.length > 1 ? '<p class="kzu-ph">' + (p * 500 + 1) + '–' + Math.min(KZN, p * 500 + 500) + '자</p>' : '') + '<div class="books">' + ps.map(kzBookHTML).join('') + '</div>').join('') +
      (all ? '<p class="kzu-ph">한자 전체 총정리</p><div class="books">' + kzBookHTML(all) + '</div>' : '');
    const done = KZCH.filter(c => { const x = kzChPeek(c.i); return x && x.n > 0; }).length, on = KZCH.some(c => { const x = kzChPeek(c.i); return !!(x && x.cur); });
    return foldHTML('kz', 'grp-kz', '한자', '1–' + KZN + '자', KZCH, inner, {done, on});
  } catch (e) { return ''; }
}

/* ----- 한자 단원 공부: 단어 공부와 같은 흐름(앞면 → 해설 → 모르겠음/알고있음 → 다음, 모르는 것만 라운드 반복·섞기) ----- */
let kctx = null, kui = {rev: false, mode: 'front', c: null, t0: 0, lock: 0}, kundo = [];
const kzRun = () => { if (!kctx) return null; const ch = kzChPeek(kctx.i); return ch ? ch.cur : null; };
function kzTouch(r, now) { r.u = now; kzChGet(kctx.i).u = now; }
function kzAddTime(r, dt) {
  if (!(dt > 0)) return;
  r.t += dt; KZ.g.tt += dt;
  const k = dayKey(Date.now()); KZ.g.d[k] = (KZ.g.d[k] || 0) + dt;
  kzChGet(kctx.i).t += dt;
}
function kzOpen(i, fresh) {
  if (!KZCH[i] || !V.kz) return;
  const ch = kzChGet(i), now = Date.now();
  let resumed = false;
  if (fresh || !ch.cur) { ch.cur = newRun(mixIds(KZCH[i]), false); ch.u = now; kzSave(); }
  else resumed = ch.cur.pos > 0 || ch.cur.ph === 'loop';
  kctx = {i}; kundo = [];
  closeModal(); closeSheet();
  show('kz'); kzEnter();
  if (resumed) toast('이어서 · ' + progText(ch.cur));
}
function kzEnter() {
  const r = kzRun();
  if (!r) { closeModal(); kctx = null; show('home'); return; }
  const c = curId(r);
  if (c == null && r.ph === 'loop' && r.next.length) { kzRoundDialog(r); return; }
  if (c == null) {
    if (r.ph === 'main' && r.unk.length) { kzLoopDialog(r); return; }
    kzFinish(r); return;
  }
  const m = mono();
  closeModal();
  kui = {rev: false, mode: 'front', c, t0: m, lock: m + 300};
  kzRender();
}
function kzPushUndo(r, c) {
  const dk = dayKey(Date.now());
  kundo.push({i: kctx.i, run: JSON.stringify(r), c, w: KZ.w[c] ? JSON.stringify(KZ.w[c]) : null, chT: kzChGet(kctx.i).t, tt: KZ.g.tt, dk, dv: KZ.g.d[dk] || 0});
  if (kundo.length > 40) kundo.shift();
}
function kzAnswer(known) {
  const now = Date.now(), m = mono();
  if (!kctx || m < kui.lock || kui.mode === 'unknown') return;
  const r = kzRun(); const c = curId(r);
  if (c == null || c !== kui.c) return;
  kzPushUndo(r, c);
  const x = kzWGet(c);
  if (r.ph === 'main') { x.n++; if (known) r.k++; else r.unk.push(c); }
  else if (!known) r.next.push(c);
  if (!known) x.m++;
  x.l = known ? 1 : 0; x.t = now; x.u = now;
  kzAddTime(r, Math.min(90e3, Math.max(0, m - kui.t0)));
  if (r.ph === 'main') r.pos++; else r.qpos++;
  kzTouch(r, now); kzSave();
  if (!known && !kui.rev) {
    kui = {rev: true, mode: 'unknown', c, t0: m, lock: m + 300};
    kzRender();
    return;
  }
  kzEnter();
}
function kzNext() {
  const now = Date.now(), m = mono();
  if (!kctx || m < kui.lock) return;
  const r = kzRun();
  if (r) { kzAddTime(r, Math.min(90e3, Math.max(0, m - kui.t0))); kzTouch(r, now); kzSave(); }
  kzEnter();
}
function kzExplain() {
  if (!kctx || kui.rev) return;
  kui.rev = true; kui.mode = 'explain'; kui.lock = mono() + 300;
  kzRender();
}
function kzUndo() {
  const s = kundo.pop();
  if (!s || !kctx || s.i !== kctx.i) { kundo = []; return; }
  const now = Date.now();
  const r = kzCleanRun(JSON.parse(s.run));
  if (!r) return;
  kzChGet(kctx.i).cur = r; kzTouch(r, now);
  const w = s.w ? kzCleanW(JSON.parse(s.w)) : {n: 0, m: 0, l: -1, t: 0, u: 0};
  w.u = now; KZ.w[s.c] = w;
  kzChGet(kctx.i).t = s.chT;
  KZ.g.tt = s.tt; KZ.g.d[s.dk] = s.dv;
  kzSave(); closeModal();
  const c = curId(r);
  kui = {rev: false, mode: 'front', c, t0: mono(), lock: mono() + 200};
  if (c == null) { kzEnter(); return; }
  kzRender();
  toast('되돌렸어요');
}
function kzLoopGo(shuf) {
  const r = kzRun(); if (!r) return;
  r.ph = 'loop'; r.shuf = shuf; r.q = shuf ? shuffled(r.unk) : r.unk.slice(); r.qpos = 0; r.next = []; r.round = 1;
  kzTouch(r, Date.now()); kzSave();
  kzEnter();
}
function kzRoundGo(shuf) {
  const r = kzRun();
  if (!r || r.ph !== 'loop' || curId(r) != null || !r.next.length) { kzEnter(); return; }
  r.shuf = shuf; r.round++; r.q = r.shuf ? shuffled(r.next) : r.next.slice(); r.next = []; r.qpos = 0;
  kzTouch(r, Date.now()); kzSave();
  toast(r.round + '라운드 · ' + r.q.length + '개 · ' + (r.shuf ? '섞어서' : '순서대로'));
  kzEnter();
}
function kzFinish(r) {
  const now = Date.now(), ch = kzChGet(kctx.i);
  ch.n++; ch.last = {pass: ch.n, k: r.k, tot: r.ord.length, r: r.round, t: r.t, at: now}; ch.cur = null; ch.u = now;
  kzSave(); kundo = [];
  kzSummary(r, {i: kctx.i, pass: ch.n, chT: ch.t});
}
function kzExit() { kctx = null; show('home'); toast('저장했어요 · 언제든 이어서 할 수 있어요'); }
function kzBarHTML(r) {
  const c = KZCH[kctx.i], ch = kzChPeek(kctx.i);
  let prog = '', ratio = 0;
  if (r) {
    if (r.ph === 'main') { prog = Math.min(r.pos + (kui.mode === 'unknown' ? 0 : 1), r.ord.length) + ' / ' + r.ord.length; ratio = r.pos / r.ord.length; }
    else { prog = '복습 ' + r.round + 'R · ' + Math.min(r.qpos + (kui.mode === 'unknown' ? 0 : 1), r.q.length) + ' / ' + r.q.length; ratio = r.q.length ? r.qpos / r.q.length : 1; }
  }
  return '<header class="sbar"><button class="tb" data-act="kzExit" aria-label="닫기 (자동 저장)">' + ICON.close + '</button>' +
    '<div class="sb-t"><b>' + kzName(kctx.i) + ' · ' + ((ch ? ch.n : 0) + 1) + '회독</b><span>한자 ' + kzRange(c) + '</span></div>' +
    '<div class="sb-p"><b id="kz-prog">' + prog + '</b><span id="kz-clock">' + fmtClock(r ? r.t : 0) + '</span></div>' +
    '<button class="tb" data-act="kzUndo" aria-label="이전 카드로 되돌리기"' + (kundo.length ? '' : ' disabled') + '>' + ICON.undo + '<span class="sm-hide">이전</span></button>' +
    (FS.ok && !STANDALONE ? '<button class="tb" data-act="full" aria-label="전체화면">' + ICON.full + '<span class="sm-hide">전체화면</span></button>' : '') +
  '</header><div class="pbar"><i style="width:' + (100 * Math.min(1, ratio)).toFixed(1) + '%"></i></div>';
}
function kzTopHTML(c, r, withMiss) {
  const x = KZ.w[c];
  return '<div class="cf-top"><span class="no">漢字 No.' + KZNO.get(c) + '</span>' +
    (r && r.ph === 'loop' ? '<span class="phase">모르는 한자 복습 · ' + r.round + '라운드</span>' : '') +
    (withMiss && x && x.m ? '<span class="miss">모르겠음 ' + x.m + '회</span>' : '') + '</div>';
}
function kzRender() {
  const r = kzRun(), c = kui.c;
  if (!r || c == null || !K[c]) { closeModal(); kctx = null; show('home'); return; }
  const gap = '<span class="ab-gap"></span>';   /* 소리 버튼 자리: 비워서 버튼 자리 고정 */
  let bar;
  if (kui.mode === 'unknown') bar = gap + '<button class="ab ab-next" data-act="kzNext">다음 →</button>';
  else if (kui.rev) bar = gap + '<button class="ab ab-ng" data-act="kzNg">' + ICON.q + '모르겠음</button><button class="ab ab-ok" data-act="kzOk">' + ICON.check + '알고있음</button>';
  else bar = '<button class="ab ab-ex" data-act="kzExplain">' + ICON.book + '해설</button><button class="ab ab-ng" data-act="kzNg">' + ICON.q + '모르겠음</button><button class="ab ab-ok" data-act="kzOk">' + ICON.check + '알고있음</button>';
  const body = kui.rev ? kzTopHTML(c, r, true) + kzBodyHTML(c)
    : kzTopHTML(c, r, false) + '<div class="cf-mid"><div class="cf-word w1 kzu-q" lang="ja">' + esc(c) + '</div></div>';
  V.kz.innerHTML = kzBarHTML(r) +
    '<div class="scroll" id="kz-sc"><div class="stage" id="kz-stage">' + body + '</div></div>' +
    '<footer class="abar"><div class="abar-in">' + bar + '</div></footer>';
  const sc = $('#kz-sc'); if (sc) sc.scrollTop = 0;
}
function kzStub(r) { V.kz.innerHTML = kzBarHTML(r) + '<div class="scroll"><div class="stage"></div></div>'; }
function kzLoopDialog(r) {
  kzStub(r);
  openModal('<div class="dlg"><div class="hanko" aria-hidden="true">復</div><h2>모르는 한자 ' + r.unk.length + '개만 모았어요</h2>' +
    '<p>' + r.ord.length + '개 중 ' + r.k + '개 알고있음(' + pct(r.k, r.ord.length) + '%). 이제 모르는 한자를 다 맞힐 때까지 반복해요.</p>' +
    '<p class="q">순서를 섞을까요?</p>' +
    '<div class="dlg-acts"><button class="btn primary" data-act="kzLoopGo" data-v="1">섞어서</button><button class="btn" data-act="kzLoopGo" data-v="0">순서대로</button></div>' +
    (kundo.length ? '<button class="link" data-act="kzUndo">마지막 답 되돌리기</button>' : '') + '</div>', false);
}
function kzRoundDialog(r) {
  kzStub(r);
  openModal('<div class="dlg"><div class="hanko" aria-hidden="true">復</div><h2>아직 모르는 한자 ' + r.next.length + '개</h2>' +
    '<p>' + r.round + '라운드 끝. ' + (r.round + 1) + '라운드로 한 번 더 봐요.</p><p class="q">순서를 섞을까요?</p>' +
    '<div class="dlg-acts"><button class="btn primary" data-act="kzRoundGo" data-v="1">섞어서</button><button class="btn" data-act="kzRoundGo" data-v="0">순서대로</button></div>' +
    (kundo.length ? '<button class="link" data-act="kzUndo">마지막 답 되돌리기</button>' : '') + '</div>', false);
}
function kzSummary(r, info) {
  const t = $('#toast'); t.hidden = true; clearTimeout(toastT);
  V.kz.innerHTML = '<header class="sbar"><button class="tb" data-act="home" aria-label="홈으로">' + ICON.close + '</button><div class="sb-t"><b>' + kzName(info.i) + ' · ' + info.pass + '회독 완료</b></div></header><div class="scroll"><div class="stage"></div></div>';
  const c = KZCH[info.i], nx = KZCH[info.i + 1] || null;
  let guide;
  if (c.kind === 'all') guide = '한자 ' + KZN + '자 전체 회독 완료. 시험까지 이 장 반복으로 굳히세요.';
  else if (c.kind === 'review') guide = kzRange(c) + ' 총정리 완료. ' + (nx ? '다음은 ' + kzName(nx.i) + '(' + kzRange(nx) + ').' : '');
  else if (nx && nx.a !== c.a) guide = kzRange(c) + ' 묶음 완성. 다음 묶음으로 — ' + kzName(nx.i) + '.';
  else guide = '잊기 전에 바로 다음 장으로 — 방금 본 한자도 다시 나와요.';
  const acts = (nx ? '<button class="btn primary" data-act="kzOpen" data-k="' + nx.i + '">' + kzName(nx.i) + ' →</button><button class="btn" data-act="kzOpen" data-k="' + info.i + '">이 장 한 번 더</button>'
      : '<button class="btn primary" data-act="kzOpen" data-k="' + info.i + '">' + kzName(info.i) + ' 한 번 더</button>') +
    '<button class="btn" data-act="home">홈으로</button>';
  const rows = '<dt>장</dt><dd>' + kzName(info.i) + ' · ' + kzRange(c) + '</dd><dt>회독</dt><dd>' + info.pass + '회독 완료</dd>' +
    '<dt>첫 판정</dt><dd>' + r.k + ' / ' + r.ord.length + ' 알고있음 (' + pct(r.k, r.ord.length) + '%)</dd>' +
    '<dt>모르는 한자</dt><dd>' + (r.ord.length - r.k) + '개' + (r.round ? ' → ' + r.round + '라운드 만에 통과' : '') + '</dd>' +
    '<dt>공부시간</dt><dd>' + fmtDur(r.t) + '</dd><dt>이 장 누적</dt><dd>' + fmtDur(info.chT) + '</dd><dt>한자 총 공부시간</dt><dd>' + fmtDur(KZ.g.tt) + '</dd>';
  openModal('<div class="dlg"><div class="hanko" aria-hidden="true">済</div><h2>수고하셨어요!</h2><dl class="sum">' + rows + '</dl><p>' + esc(guide) + '</p><div class="dlg-acts">' + acts + '</div></div>', false);
}
function kzAct(a, el) {
  const i = el.dataset.k != null ? +el.dataset.k : -1;   /* 한자 장 번호는 data-k(단어 장 data-i와 안 겹치게) */
  switch (a) {
    case 'kz': openKz(el.dataset.c, !!el.closest('#sheet')); break;
    case 'kzOpen': kzOpen(i, false); break;
    case 'kzList': if (KZCH[i]) { sheetStack = [{t: 'kzl', i}]; sheetShow(sheetStack[0]); } break;
    case 'kzRestart': { if (!KZCH[i]) break; const ch = kzChPeek(i); askConfirm(kzName(i) + '을 처음부터?', (ch && ch.cur ? '지금 ' + progText(ch.cur) + '까지 한 이번 회독을 버리고 처음부터 시작해요. ' : '') + '한자별 기록은 그대로예요.', '처음부터', () => kzOpen(i, true)); break; }
    case 'kzReset': { if (!KZCH[i]) break; askConfirm(kzName(i) + ' 기록 초기화', '이 장의 회독 수와 진행 상태를 지워요. 한자별 기록은 남아요.', '초기화', () => { KZ.ch[KZCH[i].key] = {n: 0, cur: null, t: 0, last: null, u: Date.now()}; kzSave(); closeSheet(); if (view === 'home') renderHome(); toast(kzName(i) + ' 기록을 지웠어요'); }, true); break; }
    case 'kzExit': kzExit(); break;
    case 'kzExplain': kzExplain(); break;
    case 'kzNg': kzAnswer(false); break;
    case 'kzOk': kzAnswer(true); break;
    case 'kzNext': kzNext(); break;
    case 'kzUndo': kzUndo(); break;
    case 'kzLoopGo': kzLoopGo(el.dataset.v === '1'); break;
    case 'kzRoundGo': kzRoundGo(el.dataset.v === '1'); break;
  }
}
/* 키보드(단어 공부와 같은 키): 스페이스·엔터 = 해설/다음 · 1·← = 모르겠음 · 2·→ = 알고있음/다음 · Z = 되돌리기. Esc는 공통 처리(홈으로) */
document.addEventListener('keydown', e => {
  if (view !== 'kz' || !kctx || sheetOpen || modalOpen || e.defaultPrevented) return;
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.target.closest && e.target.closest('input, textarea, select')) return;
  const k = e.key;
  if (k === 'Enter' && e.target.getAttribute && e.target.getAttribute('role') === 'button') return;   /* 공통 처리(그 버튼 누르기)에 맡김 — 단어 공부와 같은 순서 */
  if (k === ' ' || k === 'Enter') { e.preventDefault(); if (kui.mode === 'unknown') kzNext(); else if (!kui.rev) kzExplain(); }
  else if (k === '1' || k === 'ArrowLeft') { e.preventDefault(); kzAnswer(false); }
  else if (k === '2' || k === 'ArrowRight') { e.preventDefault(); if (kui.mode === 'unknown') kzNext(); else kzAnswer(true); }
  else if (k === 'z' || k === 'Z') kzUndo();
});
setInterval(() => {
  if (view !== 'kz' || !kctx || modalOpen) return;
  const el = $('#kz-clock'), r = kzRun();
  if (el && r) el.textContent = fmtClock(r.t + Math.min(90e3, Math.max(0, mono() - kui.t0)));
}, 1000);
document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible' && view === 'kz') wake(true); });

'''
rep("/* ================= 학습 화면 ================= */\n", KZ_JS + "/* ================= 학습 화면 ================= */\n")

# ---------- 시험용 손잡이 ----------
rep("window.__t = {get ui() { return ui; }, CHAPTERS, AUD, AMEM, AV, AVH, audioPrune, storyHTML, kpHTML,",
    "window.__t = {get ui() { return ui; }, CHAPTERS, AUD, AMEM, AV, AVH, audioPrune, storyHTML, kpHTML, explainHTML, KC, KZO, KZCH, kzBodyHTML, kzRun, get kui() { return kui; }, get KZ() { return KZ; }, get sheetStack() { return sheetStack; },")
