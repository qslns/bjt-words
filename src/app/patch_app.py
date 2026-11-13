#!/usr/bin/env python3
"""Create app2.tpl.html from app.tpl.html: scalable chapters, light first pass, listen mode, story blocks."""
import re
SRC = '/home/claude/work/app/app.tpl.html'
DST = '/home/claude/work/app/app2.tpl.html'
s = open(SRC, encoding='utf-8').read()
n_rep = 0
def rep(old, new, count=1):
    global s, n_rep
    c = s.count(old)
    if c != count:
        raise SystemExit(f'expected {count} match(es), found {c}: {old[:90]!r}')
    s = s.replace(old, new)
    n_rep += 1

# ---------- head ----------
rep('<meta name="description" content="BJT 빈출 500단어를 회독 방식으로 외우는 단어장">',
    '<meta name="description" content="BJT 단어를 회독 방식으로 외우는 단어장">')
rep('<title>BJT 빈출 단어장</title>', '<title>BJT 단어 회독</title>')

# ---------- CSS additions ----------
CSS_ADD = r'''
/* ---------- 가볍게 1회독 · 소리 모드 · 이야기 ---------- */
.w9,.w10{font-size:clamp(32px,min(6.6vw,10.5vh),84px);letter-spacing:0}
.w11,.w12{font-size:clamp(28px,min(5.6vw,9vh),72px);letter-spacing:0}
.ans-hw.xlong{font-size:clamp(28px,4.2vw,50px)}
.lite{width:100%;border-radius:16px;background:var(--surface);border:2px solid var(--stamp);display:flex;flex-direction:column;gap:10px;padding:16px 18px;box-shadow:var(--shadow)}
.lite-h{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.lite-h b{font-size:clamp(19px,2.3vw,24px);font-weight:700}
.lite-h span{font-size:14px;color:var(--ink-2)}
.lite-p{display:flex;align-items:center;gap:12px;font-family:var(--f-mono);font-size:15px;color:var(--ink-2);font-variant-numeric:tabular-nums}
.lite-p .lbar{flex:1;height:8px;border-radius:99px;background:var(--line-2);overflow:hidden}
.lite-p .lbar i{display:block;height:100%;background:var(--stamp)}
.lite-acts{display:flex;gap:10px;flex-wrap:wrap}
.lite-acts .btn{flex:1 1 160px}
.btn.stamp{background:var(--stamp);color:var(--on-stamp);border-color:var(--stamp)}
.part-h{font-size:13px;color:var(--ink-3);margin-top:-4px}
.lt{display:flex;flex-direction:column;gap:18px;padding-block:6px 10px}
.lt-a,.lt-b{display:contents}
.lt-head{order:1}.lt-story{order:2}.lt-pt{order:3}.lt-ex{order:4}
@media (min-width:960px){.lt{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,6fr);gap:36px;align-items:start}.lt-a,.lt-b{display:flex;flex-direction:column;gap:18px;min-width:0}}
.lt-head{display:flex;flex-direction:column;gap:4px}
.lt-word{font-family:var(--f-kyo);font-weight:500;font-size:clamp(46px,7vw,92px);line-height:1.45;letter-spacing:.03em;text-align:left;padding:2px 8px;margin-left:-8px;border-radius:14px;word-break:keep-all;overflow-wrap:anywhere;max-width:100%}
.lt-word.long{font-size:clamp(32px,5vw,62px)}
.lt-word.xlong{font-size:clamp(26px,3.8vw,46px)}
.lt-word rt{font-family:var(--f-jp);font-size:.32em;font-weight:500;color:var(--accent)}
.lt-word:active{background:var(--surface-2)}
.lt-read{font-size:clamp(20px,2.4vw,28px);color:var(--ink-2);letter-spacing:.06em}
.lt-mean{font-size:clamp(24px,3vw,36px);font-weight:700;line-height:1.3}
.lt-mean .lt-ko{display:inline-block;font-weight:600;color:var(--accent);margin-right:10px}
.story{display:flex;flex-direction:column;gap:8px;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 12px 14px}
.story .sl{font-family:var(--f-mono);font-size:11px;letter-spacing:.1em;font-weight:500;align-self:flex-start;background:var(--stamp);color:var(--on-stamp);padding:3px 8px 2px;border-radius:2px}
.lk{display:grid;grid-template-columns:46px minmax(0,1fr);gap:10px;align-items:start}
.lk-big{width:46px;height:46px;border:1px solid var(--line);border-radius:6px;display:grid;place-items:center;font-family:var(--f-kyo);font-weight:500;font-size:32px;line-height:1;background:var(--bg)}
.lk-t{display:flex;flex-direction:column;gap:1px;min-width:0}
.lk-hs{font-size:14px;color:var(--ink-2);line-height:1.45}
.lk-hs b{font-size:16px;font-weight:700;color:var(--ink);margin-right:2px}
.lk-x{font-size:15px;line-height:1.5;color:var(--ink)}
.st-w{font-size:clamp(16px,1.8vw,19px);line-height:1.65;font-weight:600;border-top:1px dashed var(--line);padding-top:10px}
.st-w::before{content:"단어 → ";color:var(--stamp);font-weight:700}
.lt-ex .jp{margin:0}
.lt-ex .ko{color:var(--ink-2)}
.lt-ex .sent{border:0;padding:4px 0 0}
.lis-btn{width:min(46vw,260px);height:min(46vw,260px);border-radius:50%;display:grid;place-items:center;background:var(--accent);color:var(--on-accent);box-shadow:var(--shadow)}
.lis-btn svg{width:42%;height:42%}
.lis-btn:active{filter:brightness(.92)}
.tb.lis[aria-pressed="true"]{background:var(--accent);color:var(--on-accent);border-color:var(--accent)}
.s-story{order:2}
'''
rep('@media (prefers-reduced-motion:no-preference){', CSS_ADD + '@media (prefers-reduced-motion:no-preference){')
rep('.s-ans{order:1}.s-pt{order:2}.s-sent{order:3}.s-pair{order:4}.s-kp{order:5}',
    '.s-ans{order:1}.s-pt{order:3}.s-sent{order:4}.s-pair{order:5}.s-kp{order:6}')

# ---------- views ----------
rep('  <section class="view" id="v-browse" hidden></section>\n',
    '  <section class="view" id="v-browse" hidden></section>\n  <section class="view" id="v-light" hidden></section>\n')

# ---------- categories + chapters ----------
rep("['formal','격식어·부사'],['kata','가타카나']];",
    "['formal','격식어·부사'],['kata','가타카나'],['keigo','경어·정형 표현'],['it','업무·시스템'],['gen','일반 어휘']];")
old_ch = s[s.index('/* 장(章): 50개씩 늘려 250'):s.index("const chName = i =>")]
new_ch = '''/* 장(章): 250개 묶음 안에서 50개씩 누적 → 500개마다 총정리 → 마지막에 전체 */
function genChapters(total) {
  const list = [];
  const add = (a, b, blk, kind) => list.push({a, b, blk, kind, part: Math.floor((a - 1) / 500)});
  for (let p = 0; p * 500 < total; p++) {
    const ps = p * 500 + 1, pe = Math.min(total, ps + 499);
    for (let bs = ps, k = 0; bs <= pe; bs += 250, k++) {
      const be = Math.min(pe, bs + 249);
      for (let e = Math.min(be, bs + 49); ; e = Math.min(be, e + 50)) { add(bs, e, k % 2 ? 'B' : 'A', 'step'); if (e >= be) break; }
    }
    if (pe - ps + 1 > 250) add(ps, pe, 'Z', 'review');
  }
  if (total > 500) add(1, total, 'Z', 'all');
  return list;
}
/* 500개 묶음마다 단어 구성 지문: 단어가 추가돼도 내용이 같은 장은 진도를 그대로 이어감 */
const PSIG = (() => { const out = []; for (let p = 0; p * 500 < TOTAL; p++) { let h = 2166136261; const part = ORDER.slice(p * 500, p * 500 + 500); for (const id of part) { h ^= id; h = Math.imul(h, 16777619) >>> 0; } out.push(h.toString(36) + '.' + part.length); } return out; })();
const chKey = (c, sig) => c.kind === 'all' ? 'all:' + sig.join(',') : sig[c.part] + ':' + c.a + '-' + c.b + ':' + c.kind;
const CHAPTERS = genChapters(TOTAL).map((c, i) => Object.assign(c, {i, ids: ORDER.slice(c.a - 1, c.b), cnt: c.b - c.a + 1, key: chKey(c, PSIG)}));
const KEY2I = new Map(CHAPTERS.map(c => [c.key, c.i]));
const LAYOUT = 'v4';
const LEGACY = {'v3:2697:60': ['zkf6ci.500', '1g6pezw.500', 'ppslt0.500', '1ytbfhm.500', 'dj9ngn.500', 'dxqmwp.197']};
function legacyKeys(lay) { const sig = LEGACY[lay]; if (!sig) return null; return genChapters(+String(lay).split(':')[1]).map(c => chKey(c, sig)); }
'''
s = s.replace(old_ch, new_ch); n_rep += 1

# ---------- exam date ----------
rep("const DEF_EXAM = '2026-10-07';", "const DEF_EXAM = '2026-10-08';")
rep("const DEF = {auto: true, rate: 1, sent: true, shuf: false, wkN: 2, furi: 'all', tr: 'show', kp: false, exam: DEF_EXAM, u: 0};",
    "const DEF = {auto: true, rate: 1, sent: true, shuf: false, wkN: 2, furi: 'all', tr: 'show', kp: false, lis: false, exam: DEF_EXAM, em: 0, u: 0};")
rep("  if (typeof o.exam === 'string' && parseDay(o.exam) != null) r.exam = o.exam;\n",
    "  if (typeof o.exam === 'string' && parseDay(o.exam) != null) r.exam = o.exam;\n  if (typeof o.lis === 'boolean') r.lis = o.lis;\n  if (o.em === 1) r.em = 1;\n")
rep("let S = Object.assign({}, DEF, cleanS(LS.get(KS)));\n",
    "let S = Object.assign({}, DEF, cleanS(LS.get(KS)));\n/* 시험일이 10/8(목) 08:00으로 바뀜: 예전 기본값(10/7)이면 한 번만 옮김 */\nif (!S.em) { if (S.exam === '2026-10-07') S.exam = '2026-10-08'; S.em = 1; LS.set(KS, S); }\n")

# ---------- progress store: layout reset + light pass ----------
rep("const blankH = () => ({ch: {}, w: {}, wr: null, wru: 0, g: {tt: 0, d: {}}, rs: 0, u: 0});",
    "const blankH = () => ({ch: {}, w: {}, wr: null, wru: 0, g: {tt: 0, d: {}}, lt: {pos: 0, done: 0, t: 0, u: 0}, lay: LAYOUT, rs: 0, u: 0});\n"
    "function cleanLt(x) { x = obj(x); let pos = Math.min(Math.floor(nn(x.pos)), Math.max(0, TOTAL - 1)); const id = +x.id; if (Number.isInteger(id) && NO.has(id)) pos = NO.get(id) - 1; return {pos, id: ORDER[pos], done: nn(x.done), t: nn(x.t), u: nn(x.u)}; }")
rep("""  const ch = obj(o.ch);
  for (const k in ch) { const i = +k; if (Number.isInteger(i) && i >= 0 && i < CHAPTERS.length) { const c = cleanCh(ch[k]); if (c) h.ch[i] = c; } }
  const w = obj(o.w);""",
"""  /* 장 기록은 장의 지문(key)으로 찾아 옮김: 내용이 바뀐 장만 비워짐. 단어 기록은 항상 그대로 */
  const ch = obj(o.ch), lk = o.lay === LAYOUT ? null : legacyKeys(o.lay);
  for (const k in ch) { const c = cleanCh(ch[k]); if (!c) continue; const key = c.k || (lk ? lk[+k] : null); const i = key != null ? KEY2I.get(key) : undefined; if (i != null) { c.k = key; h.ch[i] = c; } }
  const w = obj(o.w);""")
rep("  h.wr = cleanRun(o.wr); h.wru = nn(o.wru);\n",
    "  h.wr = cleanRun(o.wr); h.wru = nn(o.wru);\n  h.lt = cleanLt(o.lt);\n")
rep("let H = normH(LS.get(KH));\n",
    "const RAW_H = LS.get(KH);\nlet H = normH(RAW_H);\nif (RAW_H && RAW_H.lay !== LAYOUT) LS.set(KH, H);   /* 새 장 구성으로 한 번 정리해서 저장 */\n")
# mergeH: chapters only when same layout; light pass newest wins
rep("""  const rch = obj(R.ch);
  for (const k in rch) {
    const i = +k; if (!(Number.isInteger(i) && i >= 0 && i < CHAPTERS.length)) continue;
    const r = cleanCh(rch[k]); if (!r) continue;""",
"""  const rch = obj(R.ch), rlk = R.lay === LAYOUT ? null : legacyKeys(R.lay);
  const rlt = cleanLt(R.lt);
  if (rlt.u > nn(H.lt && H.lt.u)) { H.lt = rlt; res.changed = true; } else if (nn(H.lt && H.lt.u) > rlt.u) res.localNewer = true;
  for (const k in rch) {
    const r = cleanCh(rch[k]); if (!r) continue;
    const key = r.k || (rlk ? rlk[+k] : null); const i = key != null ? KEY2I.get(key) : undefined;
    if (i == null) continue; r.k = key;""")


rep("function cleanCh(x) { if (!x || typeof x !== 'object') return null; return {n: nn(x.n), cur: cleanRun(x.cur), t: nn(x.t), last: cleanLast(x.last), u: nn(x.u)}; }",
    "function cleanCh(x) { if (!x || typeof x !== 'object') return null; return {n: nn(x.n), cur: cleanRun(x.cur), t: nn(x.t), last: cleanLast(x.last), u: nn(x.u), k: typeof x.k === 'string' ? x.k : ''}; }")
rep("const chGet = i => H.ch[i] || (H.ch[i] = {n: 0, cur: null, t: 0, last: null, u: 0});",
    "const chGet = i => { const c = H.ch[i] || (H.ch[i] = {n: 0, cur: null, t: 0, last: null, u: 0, k: ''}); c.k = CHAPTERS[i].key; return c; };")
# ---------- audio: tts text + done flag versioned ----------
rep("const sayWord = id => { const w = byId.get(id); if (!w) return; if (AUD.on) AUD.play(AUD.url('w', id), w.r); else TTS.say(w.r); };",
    "const sayWord = id => { const w = byId.get(id); if (!w) return; const t = w.tw || w.r; if (AUD.on) AUD.play(AUD.url('w', id), t); else TTS.say(t); };")
rep("  const done = saved.indexOf(AUDIO_CACHE + '|') === 0;", "  const done = saved.indexOf(AUDIO_CACHE + '|' + AUDIO_TOTAL + '|') === 0;")
rep("  if (!fail) { try { localStorage.setItem('bjt500.audio', AUDIO_CACHE + '|' + Date.now()); } catch (e) {} }",
    "  if (!fail) { try { localStorage.setItem('bjt500.audio', AUDIO_CACHE + '|' + AUDIO_TOTAL + '|' + Date.now()); } catch (e) {} }")
rep("    (done ? '이 기기에 전부 저장돼 있어서 인터넷 없이도 발음이 나와요.' : '‘음성 전체 받아두기’(약 ' + AUDIO_MB + 'MB, 와이파이 권장)를 한 번 해 두면 인터넷 없이도 발음이 나와요. 안 해도 들을 때마다 받아요.');",
    "    (done ? '이 기기에 전부 저장돼 있어서 인터넷 없이도 발음이 나와요.' : '‘음성 전체 받아두기’(약 ' + AUDIO_MB + 'MB, 와이파이 권장)를 한 번 해 두면 인터넷 없이도 발음이 나와요. 예전에 받아 둔 음성은 그대로 두고 새로 생긴 것만 받아요. 안 해도 들을 때마다 받아요.');")

# ---------- views map ----------
rep("const V = {home: $('#v-home'), study: $('#v-study'), weak: $('#v-weak'), browse: $('#v-browse')};",
    "const V = {home: $('#v-home'), study: $('#v-study'), weak: $('#v-weak'), browse: $('#v-browse'), light: $('#v-light')};")
rep("  if (v !== 'study') stopVoice();", "  if (v !== 'study' && v !== 'light') stopVoice();")
rep("  wake(v === 'study');\n}", "  wake(v === 'study' || v === 'light');\n}")

# ---------- enterCard: listen mode autoplay ----------
rep("""  ui = {rev: false, mode: 'front', id, t0: m, lock: m + 300};
  renderStudy();
  warmCard(id, false);
}""", """  ui = {rev: false, mode: 'front', id, t0: m, lock: m + 300};
  renderStudy();
  warmCard(id, false);
  if (S.lis) sayWord(id);
}""")

# ---------- study bar: listen toggle ----------
rep("""    '<button class="tb" data-act="undo" aria-label="이전 카드로 되돌리기"' + (undoStack.length ? '' : ' disabled') + '>' + ICON.undo + '<span class="sm-hide">이전</span></button>' +
  '</header>""", """    '<button class="tb lis" data-act="lis" aria-pressed="' + !!S.lis + '" aria-label="소리로 맞히기 ' + (S.lis ? '끄기' : '켜기') + '">' + ICON.spk.replace('<svg ', '<svg width="21" height="21" ') + '<span class="sm-hide">소리</span></button>' +
    '<button class="tb" data-act="undo" aria-label="이전 카드로 되돌리기"' + (undoStack.length ? '' : ' disabled') + '>' + ICON.undo + '<span class="sm-hide">이전</span></button>' +
  '</header>""")

# ---------- front card: long words + listen mode ----------
rep("""  const len = Math.min(8, Math.max(1, [...w.w].length));""", """  const len = Math.min(12, Math.max(1, [...w.w].length));""")
rep("""  return '<div class="cf-top">' + tierTag(w.t) + '<span>' + esc(CAT[w.c]) + '</span><span class="no">No.' + NO.get(w.id) + '</span>' + phase + '</div>' +
    '<div class="cf-mid">' +""", """  if (S.lis) return '<div class="cf-top">' + tierTag(w.t) + '<span>' + esc(CAT[w.c]) + '</span><span class="no">No.' + NO.get(w.id) + '</span>' + phase + '</div>' +
    '<div class="cf-mid"><button class="lis-btn" data-act="sayW" aria-label="다시 듣기">' + ICON.spk + '</button>' +
      '<span class="cf-hint">듣고 뜻을 떠올려 보세요 · 누르면 다시 들어요</span></div>';
  return '<div class="cf-top">' + tierTag(w.t) + '<span>' + esc(CAT[w.c]) + '</span><span class="no">No.' + NO.get(w.id) + '</span>' + phase + '</div>' +
    '<div class="cf-mid">' +""")

# ---------- explanation: story block ----------
rep("""  return '<div class="ex"><div class="ex-a">' + ansHTML(w, inSheet) + ptHTML(w) + pairHTML(w) + kpHTML(w) + '</div><div class="ex-b">' + sentHTML(w) + '</div></div>';""",
    """  return '<div class="ex"><div class="ex-a">' + ansHTML(w, inSheet) + storyHTML(w, 's-story') + ptHTML(w) + pairHTML(w) + kpHTML(w) + '</div><div class="ex-b">' + sentHTML(w) + '</div></div>';""")
rep("""    '<div class="ans-row"><h2 class="ans-hw' + ([...w.w].length >= 6 ? ' long' : '') + '" lang="ja">'""",
    """    '<div class="ans-row"><h2 class="ans-hw' + ([...w.w].length >= 10 ? ' xlong' : [...w.w].length >= 6 ? ' long' : '') + '" lang="ja">'""")
STORY_FN = r'''
/* 이야기: 부수 → 한자 → 단어 (처음 보는 사람이 바로 이해하도록) */
function storyHTML(w, cls) {
  const ks = [...new Set(w.kj || [])].filter(c => K[c]);
  const rows = ks.map(c => {
    const k = K[c];
    const h = k.h && k.h.charAt(0) !== '?' ? k.h : (k.h ? k.h.replace(/^\?\s*/, '') : '');
    return '<div class="lk"><span class="lk-big" lang="ja">' + esc(c) + '</span><div class="lk-t">' +
      '<span class="lk-hs">' + (h ? '<b>' + esc(h) + '</b>' : '') + (k.s ? (h ? ' · ' : '') + mixJa(k.s) : '') + '</span>' +
      (k.x ? '<p class="lk-x">' + mixJa(k.x) + '</p>' : '') + '</div></div>';
  }).join('');
  const st = w.st ? '<p class="st-w">' + mixJa(w.st) + '</p>' : '';
  if (!rows && !st) return '';
  return '<section class="' + cls + ' story"><span class="sl">이야기</span>' + rows + st + '</section>';
}
'''
rep("const ptHTML = w => w.p ?", STORY_FN + "const ptHTML = w => w.p ?")

# ---------- summary dialog: generic chapter flow ----------
old_sum = s[s.index("    if (info.i === 4) guide = '앞 250 완성."):s.index("  } else {\n    rows = '<dt>복습</dt><dd>약점 단어</dd>';")]
new_sum = """    const nx = CHAPTERS[info.i + 1];
    if (c.kind === 'all') guide = TOTAL + '개 전체 회독 완료. 시험까지 약점 복습 + 이 장 반복으로 굳히세요.';
    else if (c.kind === 'review') guide = 'No.' + c.a + '–' + c.b + ' 총정리 완료. ' + (nx ? '다음은 ' + chName(nx.i) + '(No.' + nx.a + '–' + nx.b + ').' : '');
    else if (nx && nx.a !== c.a) guide = 'No.' + c.a + '–' + c.b + ' 묶음 완성. 다음 묶음으로 — ' + chName(nx.i) + '.';
    else guide = '잊기 전에 바로 다음 장으로 — 방금 본 단어도 다시 나와요.';
    acts = (nx ? '<button class="btn primary" data-act="openCh" data-i="' + nx.i + '">' + chName(nx.i) + ' 시작 →</button><button class="btn" data-act="openCh" data-i="' + info.i + '">이 장 한 번 더</button>'
      : '<button class="btn primary" data-act="openCh" data-i="' + info.i + '">' + chName(info.i) + ' 한 번 더</button>') +
      '<button class="btn" data-act="home">홈으로</button>';
"""
s = s.replace(old_sum, new_sum); n_rep += 1

# ---------- home ----------
rep("const suggestNext = () => { for (const c of CHAPTERS) { const ch = H.ch[c.i]; if (!ch || ch.n === 0) return c.i; } return 10; };",
    "const suggestNext = () => { for (const c of CHAPTERS) { const ch = H.ch[c.i]; if (!ch || ch.n === 0) return c.i; } return CHAPTERS.length - 1; };")
old_home = s[s.index("    '<header class=\"bar\"><div class=\"brand\"><b>BJT</b><span>빈출 500</span></div>'"):s.index("/* ================= 학습 화면 ================= */")]
new_home = r"""    '<header class="bar"><div class="brand"><b>BJT</b><span>단어 회독 ' + TOTAL.toLocaleString() + '</span></div>' +
      '<span class="dchip" title="' + (exD.getUTCMonth() + 1) + '/' + exD.getUTCDate() + '(' + WD[exD.getUTCDay()] + ') 시험">' + ddTxt + '</span><div class="grow"></div>' +
      (FS.ok && !STANDALONE ? '<button class="tb" data-act="full" aria-label="전체화면">' + ICON.full + '<span class="sm-hide">전체화면</span></button>' : '') +
      '<button class="tb" data-act="settings" aria-label="설정">' + ICON.gear + '</button></header>' +
    '<div class="scroll"><div class="wrap home">' + installHint() + liteHTML() + banner + partsHTML() +
      '<section class="grp"><div class="zrow"><div class="side"><button class="btn big" data-act="weakView"><span>★ 약점 단어</span><small>' + wk + '개</small></button>' +
        '<button class="btn big" data-act="browse"><span>전체 단어 목록</span><small>' + TOTAL.toLocaleString() + '</small></button></div>' +
        '<div class="side"><div class="stats"><span>본 단어 <b>' + seen + '</b>/' + TOTAL + '</span><span>마지막 판정 앎 <b>' + okN + '</b></span><span>끝낸 장 <b>' + done + '</b>/' + CHAPTERS.length + '</span><span>오늘 <b>' + fmtDur(today) + '</b></span><span>총 <b>' + fmtDur(H.g.tt) + '</b></span></div></div>' +
      '</div></section>' +
      '<details class="guide"><summary>이렇게 쓰세요</summary><ol>' +
        '<li><b>번호가 앞일수록 BJT 핵심</b>이에요. 시간이 모자라면 앞에서부터.</li>' +
        '<li><b>가볍게 1회독</b>: 처음 보는 단어를 부수 → 한자 → 단어 이야기와 함께 한 번씩 훑어요. 반복 없음. 먼저 이걸로 전체를 한 번 보세요.</li>' +
        '<li><b>회독 장</b>: 第1章부터 차례대로. 250개 묶음 안에서 50개씩 늘려 가며 앞 단어를 계속 다시 봐요. 500개마다 총정리 장이 있어요.</li>' +
        '<li>카드마다 <b>알고있음</b> / <b>모르겠음</b>. 모르는 단어는 장 끝에 다 맞힐 때까지 반복. 위쪽 <b>소리</b> 버튼을 켜면 글자 없이 발음만 듣고 맞혀요(청해 연습).</li>' +
        '<li>' + S.wkN + '번 이상 모르겠음 누른 단어는 <b>약점 단어</b>에 자동으로 모여요. ★로 직접 넣고 뺄 수도 있어요.</li>' +
        '<li>중간에 닫아도 자동 저장. 장 카드의 <b>↺</b>로 그 장을 처음부터 다시.</li>' +
      '</ol></details>' +
      '<div class="sync ' + Sync.state + '"><i></i><span>' + syncTxt + '</span></div>' +
    '</div></div>';
}
function liteHTML() {
  const lt = H.lt || {pos: 0, done: 0};
  const started = lt.pos > 0 || lt.done > 0;
  const p = Math.min(lt.pos + 1, TOTAL);
  return '<section class="lite"><div class="lite-h"><b>가볍게 1회독</b><span>처음부터 끝까지 한 번씩 · 반복 없음 · 부수→한자→단어 이야기' + (lt.done ? ' · ' + lt.done + '번 완주' : '') + '</span></div>' +
    '<div class="lite-p"><span>No.' + p.toLocaleString() + ' / ' + TOTAL.toLocaleString() + '</span><span class="lbar"><i style="width:' + (100 * lt.pos / TOTAL).toFixed(1) + '%"></i></span><span>' + pct(lt.pos, TOTAL) + '%</span></div>' +
    '<div class="lite-acts"><button class="btn stamp big" data-act="ltGo">' + (started ? '이어서 · No.' + p : '시작하기') + ' →</button>' +
      (started ? '<button class="btn big" data-act="ltRestart">처음부터</button>' : '') + '</div></section>';
}
function partsHTML() {
  const parts = [];
  for (const c of CHAPTERS) { if (c.kind === 'all') continue; (parts[c.part] = parts[c.part] || []).push(c); }
  const lab = ['핵심', '중요', '확장', '보충', '보충', '보충'];
  let out = parts.map((cs, p) => {
    const a = p * 500 + 1, b = Math.min(TOTAL, a + 499);
    return '<section class="grp"><div class="grp-h"><b>' + (p + 1) + '부 · ' + (lab[p] || '보충') + '</b><span>No.' + a + '–' + b + '</span><i class="rule"></i></div>' +
      '<p class="part-h">250개씩 50개 단위로 쌓아 가며 회독 → 마지막 장은 ' + a + '–' + b + ' 총정리</p>' +
      '<div class="books">' + cs.map(c => bookHTML(c)).join('') + '</div></section>';
  }).join('');
  const all = CHAPTERS.find(c => c.kind === 'all');
  if (all) out += '<section class="grp"><div class="grp-h"><b>전체 총정리</b><span>No.1–' + TOTAL + '</span><i class="rule"></i></div><div class="books">' + bookHTML(all) + '</div></section>';
  return out;
}

/* ================= 가볍게 1회독 ================= */
let lt0 = 0;
function ltSave() { H.lt.id = ORDER[H.lt.pos]; H.lt.u = Date.now(); saveH(); }
function ltTime() { const m = mono(); if (lt0) { const dt = Math.min(90e3, Math.max(0, m - lt0)); H.lt.t += dt; H.g.tt += dt; const k = dayKey(Date.now()); H.g.d[k] = (H.g.d[k] || 0) + dt; } lt0 = m; }
function openLight(fresh) {
  if (!H.lt) H.lt = {pos: 0, done: 0, t: 0, u: 0};
  if (fresh) H.lt.pos = 0;
  H.lt.pos = Math.min(Math.max(0, H.lt.pos), TOTAL - 1);
  ltSave(); closeModal(); closeSheet();
  lt0 = mono();
  show('light'); renderLight(true);
}
function lightMove(d) {
  const m = mono();
  if (m < ui.lock) return;
  ui.lock = m + 250;
  ltTime(); stopVoice();
  const np = H.lt.pos + d;
  if (np < 0) { toast('첫 단어예요'); return; }
  if (np >= TOTAL) {
    H.lt.done++; H.lt.pos = 0; ltSave();
    openModal('<div class="dlg"><div class="hanko" aria-hidden="true">済</div><h2>전체 1회독 끝!</h2><p>' + TOTAL.toLocaleString() + '개를 한 번씩 다 봤어요. 이제 회독 장으로 넘어가서 알고있음/모르겠음으로 굳혀요.</p>' +
      '<div class="dlg-acts"><button class="btn primary" data-act="openCh" data-i="' + suggestNext() + '">' + chName(suggestNext()) + ' 시작 →</button><button class="btn" data-act="home">홈으로</button></div></div>', false);
    return;
  }
  H.lt.pos = np; ltSave();
  renderLight(true);
}
function renderLight(play) {
  const id = ORDER[H.lt.pos], w = byId.get(id);
  if (!w) { show('home'); return; }
  const weak = isWeak(id);
  const n = [...w.w].length;
  const e = w.e[0];
  V.light.innerHTML = '<header class="sbar"><button class="tb" data-act="ltExit" aria-label="닫기 (자동 저장)">' + ICON.close + '</button>' +
      '<div class="sb-t"><b>가볍게 1회독</b><span>반복 없이 한 번씩</span></div>' +
      '<div class="sb-p"><b>' + (H.lt.pos + 1).toLocaleString() + ' / ' + TOTAL.toLocaleString() + '</b><span>' + pct(H.lt.pos + 1, TOTAL) + '%</span></div>' +
      '<button class="tb star" data-act="ltStar" aria-pressed="' + weak + '" aria-label="약점 단어에 ' + (weak ? '서 빼기' : ' 넣기') + '">' + (weak ? ICON.star : ICON.starO) + '</button></header>' +
    '<div class="pbar"><i style="width:' + (100 * (H.lt.pos + 1) / TOTAL).toFixed(2) + '%"></i></div>' +
    '<div class="scroll" id="lsc"><div class="stage' + modeCls() + '"><div class="cf-top">' + tierTag(w.t) + '<span>' + esc(CAT[w.c] || '') + '</span><span class="no">No.' + NO.get(id) + '</span></div>' +
      '<div class="lt"><div class="lt-a">' +
        '<section class="lt-head"><button class="lt-word' + (n >= 10 ? ' xlong' : n >= 6 ? ' long' : '') + '" data-act="sayW" data-id="' + id + '" lang="ja" aria-label="발음 듣기">' + headRuby(w) + '</button>' +
          (w.r !== w.w ? '<div class="lt-read" lang="ja">' + esc(w.r) + '</div>' : '') +
          '<div class="lt-mean">' + (w.ko ? '<span class="lt-ko">' + esc(w.ko) + '</span>' : '') + mixJa(w.m) + '</div></section>' +
        storyHTML(w, 'lt-story') +
      '</div><div class="lt-b">' +
        (w.p ? '<section class="lt-pt pt"><span class="pt-l">BJT 포인트</span><p>' + mixJa(w.p) + '</p>' + (w.o ? '<p class="note">어원 · ' + mixJa(w.o) + '</p>' : '') + '</section>' : '') +
        (e ? '<section class="lt-ex"><h3 class="sec-h"><span>예문</span><i class="rule"></i></h3><article class="sent"><div class="sent-h"><span class="scene"><b>' + (SCENE[e.s] || ['', ''])[0] + '</b>' + esc((SCENE[e.s] || ['', e.s])[1]) + '</span>' +
          (CAN_SPEAK() ? '<button class="spk" data-act="sayS" data-id="' + id + '" data-i="0" aria-label="예문 듣기">' + ICON.spk + '</button>' : '') + '</div>' +
          '<p class="jp" lang="ja" data-act="peek">' + ruby(e.j) + '</p><p class="ko" data-act="peek">' + esc(e.k) + '</p></article></section>' : '') +
      '</div></div></div></div>' +
    '<footer class="abar"><div class="abar-in"><button class="ab ab-ng" data-act="ltPrev" aria-label="이전 단어">← 이전</button><button class="ab ab-ok" data-act="ltNext" aria-label="다음 단어">다음 →</button></div></footer>';
  const sc = $('#lsc'); if (sc) sc.scrollTop = 0;
  if (AUD.on) AUD.warm([AUD.url('w', id), AUD.url('s', id, 0)].concat(ORDER[H.lt.pos + 1] != null ? [AUD.url('w', ORDER[H.lt.pos + 1])] : []));
  if (play && S.auto) sayWord(id);
}

"""
s = s.replace(old_home, new_home); n_rep += 1

# ---------- events ----------
rep("    case 'undo': undo(); break;\n",
    "    case 'undo': undo(); break;\n"
    "    case 'lis': { setS({lis: !S.lis}); if (view === 'study' && ctx && ui.id != null) { renderStudy(); if (S.lis && !ui.rev) sayWord(ui.id); } toast(S.lis ? '소리 모드: 발음만 듣고 맞혀요' : '소리 모드를 껐어요'); break; }\n"
    "    case 'ltGo': openLight(false); break;\n"
    "    case 'ltRestart': askConfirm('가볍게 1회독을 처음부터?', '지금 위치(No.' + (H.lt.pos + 1) + ')를 버리고 No.1부터 다시 봐요. 단어 기록과 약점은 그대로예요.', '처음부터', () => openLight(true)); break;\n"
    "    case 'ltNext': lightMove(1); break;\n"
    "    case 'ltPrev': lightMove(-1); break;\n"
    "    case 'ltExit': ltTime(); ltSave(); Sync.flushNow(); stopVoice(); show('home'); toast('저장했어요 · No.' + (H.lt.pos + 1) + '부터 이어서 할 수 있어요'); break;\n"
    "    case 'ltStar': { const id = ORDER[H.lt.pos]; const on = !isWeak(id); setWeak(id, on); renderLight(false); toast(on ? '약점 단어에 넣었어요' : '약점 단어에서 뺐어요'); break; }\n")
rep("    case 'resetAll': askConfirm('모든 진도를 지울까요?', '11개 장의 회독 기록, 단어별 기록, 약점 목록이 전부 사라져요. 되돌릴 수 없어요.',",
    "    case 'resetAll': askConfirm('모든 진도를 지울까요?', CHAPTERS.length + '개 장의 회독 기록, 가볍게 1회독 위치, 단어별 기록, 약점 목록이 전부 사라져요. 되돌릴 수 없어요.',")
rep("  if (view !== 'study' || sheetOpen || modalOpen || !ctx) return;",
    "  if (view === 'light' && !sheetOpen && !modalOpen) { if (k === 'ArrowRight' || k === ' ' || k === 'Enter') { e.preventDefault(); lightMove(1); } else if (k === 'ArrowLeft') { e.preventDefault(); lightMove(-1); } else if (k === 'r' || k === 'R') sayWord(ORDER[H.lt.pos]); return; }\n"
    "  if (view !== 'study' || sheetOpen || modalOpen || !ctx) return;")
rep("  if (k === 'Escape') { if (modalOpen && modalDismiss) closeModal(); else if (sheetOpen) closeSheet(); else if (view !== 'home' && !modalOpen) { if (view === 'study') act('exit', document.body); else show('home'); } return; }",
    "  if (k === 'Escape') { if (modalOpen && modalDismiss) closeModal(); else if (sheetOpen) closeSheet(); else if (view !== 'home' && !modalOpen) { if (view === 'study') act('exit', document.body); else if (view === 'light') act('ltExit', document.body); else show('home'); } return; }")
# light pass time when leaving page
rep("  if (document.visibilityState === 'hidden') { Sync.flushNow(); stopVoice(); }",
    "  if (document.visibilityState === 'hidden') { if (view === 'light') { ltTime(); ltSave(); lt0 = 0; } Sync.flushNow(); stopVoice(); }")
rep("  else { if (view === 'study') wake(true); onDataChanged(); }",
    "  else { if (view === 'study' || view === 'light') wake(true); if (view === 'light') lt0 = mono(); onDataChanged(); }")
# settings: card front mode
rep("      '<section><h3>카드 앞면</h3>' + segB('setSent', S.sent, [[true, '예문 같이 보기'], [false, '단어만']]) +",
    "      '<section><h3>카드 앞면</h3>' + segB('setLis', S.lis, [[false, '글자 보고 맞히기'], [true, '소리만 듣고 맞히기']]) + segB('setSent', S.sent, [[true, '예문 같이 보기'], [false, '단어만']]) +")
rep("    case 'setSent': setS({sent: el.dataset.v === 'true'}); openSettings(); break;\n",
    "    case 'setSent': setS({sent: el.dataset.v === 'true'}); openSettings(); break;\n    case 'setLis': setS({lis: el.dataset.v === 'true'}); openSettings(); break;\n")
rep("      '<section><h3>발음</h3>' + segB('setAuto', S.auto, [[true, '해설 열 때 자동 발음'], [false, '누를 때만']]) +",
    "      '<section><h3>발음</h3>' + segB('setAuto', S.auto, [[true, '해설·1회독에서 자동 발음'], [false, '누를 때만']]) +")

# ---------- 일본어 글씨체: BJT CBT 화면과 같게 (지문·자료 = 명조, 문제·선택지 = 고딕) ----------
rep('family=Klee+One:wght@600&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap',
    'family=BIZ+UDPMincho:wght@400;700&family=BIZ+UDPGothic:wght@400;700&display=swap')
MINCHO = '"Hiragino Mincho ProN","Hiragino Mincho Pro","YuMincho","Yu Mincho","BIZ UDPMincho","MS PMincho","Noto Serif JP","Noto Serif CJK JP",serif'
GOTHIC = '"Hiragino Kaku Gothic ProN","Hiragino Sans","BIZ UDPGothic","MS PGothic","Yu Gothic","Noto Sans JP","Noto Sans CJK JP",sans-serif'
rep('--f-jp:"Zen Kaku Gothic New","Hiragino Sans","Hiragino Kaku Gothic ProN","Noto Sans JP","Noto Sans CJK JP","Yu Gothic",sans-serif;',
    '--f-jp:' + MINCHO + ';')
rep('--f-kyo:"Klee One","Klee","YuKyokasho","Hiragino Mincho ProN","Yu Mincho","Noto Serif JP","Noto Serif CJK JP",serif;',
    '--f-kyo:' + MINCHO + ';')
rep('<style>\n:root{', '<style>\nbody.jf-g{--f-jp:' + GOTHIC + ';--f-kyo:' + GOTHIC + '}\n:root{')
rep('.cf-word{font-family:var(--f-kyo);font-weight:600', '.cf-word{font-family:var(--f-kyo);font-weight:500')
rep('.ans-hw{font-family:var(--f-kyo);font-weight:600', '.ans-hw{font-family:var(--f-kyo);font-weight:500')
rep('.rw .w{font-family:var(--f-kyo);font-weight:600', '.rw .w{font-family:var(--f-kyo);font-weight:500')
s = re.sub(r'(\.kc-big\{[^}]*?)font-weight:600', r'\1font-weight:500', s, count=1)
rep("const DEF = {auto: true, rate: 1, sent: true, shuf: false, wkN: 2, furi: 'all', tr: 'show', kp: false, lis: false, exam: DEF_EXAM, em: 0, u: 0};",
    "const DEF = {auto: true, rate: 1, sent: true, shuf: false, wkN: 2, furi: 'all', tr: 'show', kp: false, lis: false, jf: 'm', exam: DEF_EXAM, em: 0, u: 0};")
rep("  if (typeof o.lis === 'boolean') r.lis = o.lis;\n",
    "  if (typeof o.lis === 'boolean') r.lis = o.lis;\n  if (o.jf === 'm' || o.jf === 'g') r.jf = o.jf;\n")
rep("if (!S.em) { if (S.exam === '2026-10-07') S.exam = '2026-10-08'; S.em = 1; LS.set(KS, S); }\n",
    "if (!S.em) { if (S.exam === '2026-10-07') S.exam = '2026-10-08'; S.em = 1; LS.set(KS, S); }\n"
    "const applyJf = () => document.body.classList.toggle('jf-g', S.jf === 'g');\napplyJf();\n")
rep("      '<section><h3>해설 표시</h3>' + segB('setFuri', S.furi,",
    "      '<section><h3>일본어 글씨체</h3>' + segB('setJf', S.jf, [['m', '명조 · BJT 지문·자료'], ['g', '고딕 · BJT 문제·선택지']]) + '<p class=\"hint\">실제 BJT(CBT) 화면은 문서·메일 같은 자료가 명조, 문제 문장과 선택지가 고딕이에요.</p></section>' +\n      '<section><h3>해설 표시</h3>' + segB('setFuri', S.furi,")
rep("    case 'setFuri': setS({furi: el.dataset.v}); openSettings(); refreshStage(); break;\n",
    "    case 'setFuri': setS({furi: el.dataset.v}); openSettings(); refreshStage(); break;\n    case 'setJf': setS({jf: el.dataset.v}); applyJf(); openSettings(); break;\n")

# ======================================================================
# 10/5: 약점 단어 전체·선택 삭제 / 업데이트가 확실히 들어오게 / 버전 표시 / 미니멀(흑백) 화면
# ======================================================================
rep("const B = {q: '', tier: 'all', st: 'all', cat: 'all', mask: false, wmask: false, smask: false};",
    "const B = {q: '', tier: 'all', st: 'all', cat: 'all', mask: false, wmask: false, smask: false, wsel: false, wpick: new Set()};\n"
    "let swPending = false, swReload = false;\n"
    "function applyUpdate() { if (swReload) return; swReload = true; try { if (view === 'light') { ltTime(); ltSave(); } Sync.flushNow(); } catch (e) {} location.reload(); }")
rep("  if (v === 'home') renderHome();\n  if (v === 'weak') renderWeak();",
    "  if (v === 'home' && swPending && !modalOpen) { applyUpdate(); return; }\n  if (v === 'home') renderHome();\n  if (v === 'weak') renderWeak();")
_a = s.index('function rowHTML(id, withDel) {')
_b = s.index('/* ================= 전체 단어 목록 ================= */')
s = s[:_a] + r"""function rowHTML(id, withDel, pick) {
  const w = byId.get(id), x = H.w[id], st = stOf(id);
  const on = pick && B.wpick.has(id);
  return '<li' + (pick ? ' class="pk' + (on ? ' on' : '') + '"' : '') + '><button class="row" data-act="' + (pick ? 'wpick' : 'row') + '" data-id="' + id + '"' + (pick ? ' aria-pressed="' + on + '"' : '') + '><span class="num">' + (pick ? '<i class="ck"></i>' : NO.get(id)) + '</span>' +
    '<span class="rw"><span class="w" lang="ja">' + esc(w.w) + '</span>' + (w.r !== w.w ? '<span class="r" lang="ja">' + esc(w.r) + '</span>' : '') + '</span>' +
    '<span class="rm">' + mixJa(w.m) + '</span><span class="rd">' + (x && x.m ? '<span class="miss">×' + x.m + '</span>' : '') + '<i class="dot st-' + st + '" title="' + ST_NAME[st] + '"></i></span></button>' +
    (withDel && !pick ? '<button class="del" data-act="wdel" data-id="' + id + '" aria-label="' + esc(w.w) + ' 약점에서 삭제">삭제</button>' : '') + '</li>';
}
function wselBar() {
  const n = B.wpick.size, ids = weakIds();
  const t = $('#wsel-n'); if (t) t.textContent = n + '개 선택';
  const d = $('#wsel-del'); if (d) { d.disabled = !n; d.textContent = '선택 삭제' + (n ? ' (' + n + ')' : ''); }
  const a = $('#wsel-all'); if (a) a.textContent = n && n === ids.length ? '선택 해제' : '모두 선택';
}
function weakDrop(ids, all) {
  const prev = {}, now = Date.now();
  for (const id of ids) prev[id] = H.w[id] ? JSON.stringify(H.w[id]) : null;
  const prevWr = all && H.wr ? JSON.stringify(H.wr) : null;
  for (const id of ids) { const x = wsGet(id); x.pin = 0; x.rm = x.m; x.u = now; }
  if (all) { H.wr = null; H.wru = now; }
  saveH(); B.wsel = false; B.wpick = new Set();
  if (view === 'weak') renderWeak();
  toast(ids.length + '개를 약점에서 뺐어요', '되돌리기', () => {
    const t = Date.now();
    for (const id of ids) { const q = prev[id] ? JSON.parse(prev[id]) : null; if (q) { const x = cleanW(q); x.u = t; H.w[id] = x; } }
    if (prevWr) { H.wr = cleanRun(JSON.parse(prevWr)); H.wru = t; }
    saveH(); if (view === 'weak') renderWeak(); else if (view === 'home') renderHome();
  });
}
function renderWeak() {
  const ids = weakIds(), wr = H.wr;
  if (!ids.length) B.wsel = false;
  const sc = V.weak.querySelector('.scroll'), top = sc ? sc.scrollTop : 0;
  const sel = B.wsel;
  for (const id of [...B.wpick]) if (!ids.includes(id)) B.wpick.delete(id);
  const tools = sel
    ? '<div class="wtools"><span class="wsel-n" id="wsel-n">' + B.wpick.size + '개 선택</span><div class="grow"></div>' +
        '<button class="btn" id="wsel-all" data-act="wselAll">' + (B.wpick.size && B.wpick.size === ids.length ? '선택 해제' : '모두 선택') + '</button>' +
        '<button class="btn danger" id="wsel-del" data-act="wdelSel"' + (B.wpick.size ? '' : ' disabled') + '>선택 삭제' + (B.wpick.size ? ' (' + B.wpick.size + ')' : '') + '</button>' +
        '<button class="btn" data-act="wselOff">취소</button></div>'
    : '<div class="wtools">' + (wr ? '<button class="btn primary big" data-act="weakGo">이어서 · ' + progText(wr) + '</button><button class="btn big" data-act="weakNew"' + (ids.length ? '' : ' disabled') + '>처음부터 (' + ids.length + '개 섞어서)</button>'
        : '<button class="btn primary big" data-act="weakNew"' + (ids.length ? '' : ' disabled') + '>카드로 복습 · ' + ids.length + '개 섞어서</button>') +
        (ids.length ? '<div class="grow"></div><button class="btn" data-act="wselOn">선택 삭제</button><button class="btn" data-act="wdelAll">전체 삭제</button>' : '') + '</div>';
  V.weak.innerHTML = '<header class="bar"><button class="tb" data-act="home" aria-label="홈으로">' + ICON.back + '<span class="sm-hide">홈</span></button><h1 class="bar-title">약점 단어 ' + ids.length + '</h1><div class="grow"></div>' +
    '<button class="tb" data-act="wmask" aria-pressed="' + B.wmask + '">뜻 가리기</button></header>' +
    '<div class="scroll"><div class="wrap">' + tools +
      (sel ? '<p class="note" style="margin:4px 0 12px">뺄 단어를 눌러서 고르세요.</p>'
           : '<p class="note" style="margin:4px 0 12px">' + S.wkN + '번 이상 ‘모르겠음’ 누른 단어와 ★로 넣은 단어가 모여요. 많이 틀린 순. 다 외운 단어는 ‘삭제’(다시 ' + S.wkN + '번 틀리면 돌아와요).</p>') +
      (ids.length ? '<ul class="list' + (B.wmask ? ' masked' : '') + (sel ? ' picking' : '') + '" id="wlist">' + ids.map(id => rowHTML(id, true, sel)).join('') + '</ul>' : '<p class="empty-note">아직 없어요. 회독하다가 ' + S.wkN + '번 이상 모르겠음 누른 단어가 여기에 쌓여요.</p>') +
    '</div></div>';
  const sc2 = V.weak.querySelector('.scroll'); if (sc2 && top) sc2.scrollTop = top;
}

""" + s[_b:]
rep("    case 'toastAct': { const f = toastFn; toastFn = null; $('#toast').hidden = true; if (f) f(); break; }",
    "    case 'wselOn': B.wsel = true; B.wpick = new Set(); renderWeak(); break;\n"
    "    case 'wselOff': B.wsel = false; B.wpick = new Set(); renderWeak(); break;\n"
    "    case 'wpick': { if (idAttr == null) break; if (B.wpick.has(idAttr)) B.wpick.delete(idAttr); else B.wpick.add(idAttr); const li = el.closest('li'); if (li) li.classList.toggle('on', B.wpick.has(idAttr)); el.setAttribute('aria-pressed', B.wpick.has(idAttr)); wselBar(); break; }\n"
    "    case 'wselAll': { const ids = weakIds(); B.wpick = B.wpick.size === ids.length ? new Set() : new Set(ids); renderWeak(); break; }\n"
    "    case 'wdelSel': { const ids = [...B.wpick].filter(isWeak); if (!ids.length) break; askConfirm(ids.length + '개를 약점에서 뺄까요?', '단어별 기록(앎·모름)은 그대로예요. 다시 ' + S.wkN + '번 모르면 돌아와요.', '빼기', () => weakDrop(ids, false), true); break; }\n"
    "    case 'wdelAll': { const ids = weakIds(); if (!ids.length) break; askConfirm('약점 단어 ' + ids.length + '개를 전부 뺄까요?', '단어별 기록(앎·모름)은 그대로예요. 진행 중인 약점 복습도 끝나요. 다시 ' + S.wkN + '번 모르면 돌아와요.', '전부 빼기', () => weakDrop(ids, true), true); break; }\n"
    "    case 'toastAct': { const f = toastFn; toastFn = null; $('#toast').hidden = true; if (f) f(); break; }")
# 업데이트: 열 때·돌아올 때 새 버전 확인 → 새 버전이 오면 홈에서는 바로, 학습 중이면 토스트로
rep("    window.addEventListener('load', () => { navigator.serviceWorker.register('sw.js').catch(() => {}); });",
    "    const hadCtl = !!navigator.serviceWorker.controller;\n"
    "    window.addEventListener('load', () => {\n"
    "      navigator.serviceWorker.register('sw.js').then(reg => {\n"
    "        const check = () => { reg.update().catch(() => {}); };\n"
    "        document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') check(); });\n"
    "        setInterval(check, 20 * 60 * 1000);\n"
    "      }).catch(() => {});\n"
    "    });\n"
    "    navigator.serviceWorker.addEventListener('controllerchange', () => {\n"
    "      if (!hadCtl || swReload) return;\n"
    "      swPending = true;\n"
    "      if (view === 'home' && !modalOpen && !sheetOpen) applyUpdate();\n"
    "      else toast('새 버전이 준비됐어요', '지금 적용', applyUpdate);\n"
    "    });")
# 버전 표시
rep("const MODE = '__APP_MODE__';", "const MODE = '__APP_MODE__';\nconst BUILD = '__BUILD__';")
rep("      '<div class=\"sync ' + Sync.state + '\"><i></i><span>' + syncTxt + '</span></div>' +",
    "      '<div class=\"sync ' + Sync.state + '\"><i></i><span>' + syncTxt + '</span></div>' +\n"
    "      '<p class=\"ver\">앱 버전 ' + BUILD + ' · 단어 ' + TOTAL.toLocaleString() + '개</p>' +")
MINIMAL = r"""
/* ---------- 미니멀: 흑백 + 회색 단계만 (10/5) ---------- */
:root{
  --bg:#FFFFFF;--surface:#FFFFFF;--surface-2:#F2F2F2;
  --ink:#111111;--ink-2:#555555;--ink-3:#8A8A8A;
  --line:#E2E2E2;--line-2:#EFEFEF;
  --accent:#111111;--on-accent:#FFFFFF;--fill:#111111;--on-fill:#FFFFFF;
  --stamp:#111111;--on-stamp:#FFFFFF;
  --ng:#B3261E;--ng-bg:#FFFFFF;--ok:#111111;--ok-bg:#FFFFFF;
  --bkA:#FFFFFF;--bkA2:#FFFFFF;--bkB:#FFFFFF;--bkB2:#FFFFFF;--bkZ:#FFFFFF;--bkZ2:#FFFFFF;
  --on-bk:#111111;--on-bk2:#8A8A8A;--ribbon:#111111;--on-ribbon:#FFFFFF;
  --tg:transparent;--mask:#ECECEC;--scrim:rgba(0,0,0,.35);--shadow:none;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#111111;--surface:#181818;--surface-2:#232323;
  --ink:#EDEDED;--ink-2:#A6A6A6;--ink-3:#767676;
  --line:#2E2E2E;--line-2:#242424;
  --accent:#EDEDED;--on-accent:#111111;--fill:#EDEDED;--on-fill:#111111;
  --stamp:#EDEDED;--on-stamp:#111111;
  --ng:#F2B8B5;--ng-bg:#181818;--ok:#EDEDED;--ok-bg:#181818;
  --bkA:#181818;--bkA2:#181818;--bkB:#181818;--bkB2:#181818;--bkZ:#181818;--bkZ2:#181818;
  --on-bk:#EDEDED;--on-bk2:#767676;--ribbon:#EDEDED;--on-ribbon:#111111;
  --tg:transparent;--mask:#262626;--scrim:rgba(0,0,0,.6);--shadow:none}}
:root[data-theme="dark"]{
  --bg:#111111;--surface:#181818;--surface-2:#232323;
  --ink:#EDEDED;--ink-2:#A6A6A6;--ink-3:#767676;
  --line:#2E2E2E;--line-2:#242424;
  --accent:#EDEDED;--on-accent:#111111;--fill:#EDEDED;--on-fill:#111111;
  --stamp:#EDEDED;--on-stamp:#111111;
  --ng:#F2B8B5;--ng-bg:#181818;--ok:#EDEDED;--ok-bg:#181818;
  --bkA:#181818;--bkA2:#181818;--bkB:#181818;--bkB2:#181818;--bkZ:#181818;--bkZ2:#181818;
  --on-bk:#EDEDED;--on-bk2:#767676;--ribbon:#EDEDED;--on-ribbon:#111111;
  --tg:transparent;--mask:#262626;--scrim:rgba(0,0,0,.6);--shadow:none}
.dchip{background:transparent;color:var(--ink);border:1px solid var(--ink);font-weight:600}
.resume{background:var(--surface);color:var(--ink);border:1px solid var(--ink)}
.resume:active{filter:none;background:var(--surface-2)}
.book{border:1px solid var(--line)}
.book.blkZ{border-color:var(--ink)}
.book .spine{display:none}
.book:active{filter:none;background:var(--surface-2)}
.b-acts{left:0}
.b-btn{border:1px solid var(--line);color:var(--ink-2)}
.b-btn:active{background:var(--surface-2)}
.ribbon{top:0;clip-path:none;border-radius:0 0 8px 0;padding:3px 10px;font-size:12px;font-weight:600}
.lite{border:1px solid var(--line)}
.lite-p .lbar{height:4px}
.pt{border-color:var(--line)}
.pt-l,.story .sl{background:transparent;color:var(--ink-3);padding:0;border-radius:0;letter-spacing:.12em}
.st-w::before{color:var(--ink-3)}
.rad{color:var(--ink)}
.hanko{border-color:var(--ink-3);color:var(--ink-3)}
.lt-mean .lt-ko{color:var(--ink-2)}
.ans-hw rt,.lt-word rt{color:var(--ink-3)}
.tg{background:none;font-weight:700;text-decoration:underline;text-decoration-thickness:2px;text-underline-offset:.24em}
.ab{box-shadow:none;border:1px solid var(--line)}
.ab:active{transform:none;background:var(--surface-2)}
.ab-ex,.ab-ng{background:var(--surface);color:var(--ink)}
.ab-ok,.ab-next{background:var(--fill);color:var(--on-fill);border-color:var(--fill)}
.ab-ok:active,.ab-next:active{background:var(--fill);opacity:.85}
.phase{background:transparent;color:var(--ink-2);border:1px solid var(--line)}
.star[aria-pressed="true"],.starw[aria-pressed="true"]{color:var(--ink);border-color:var(--ink)}
.miss{color:var(--ink-3)}
.del{color:var(--ink-2)}
.del:active{background:var(--surface-2)}
.st-ok{background:var(--ink)}.st-ng{background:var(--ink-3)}
.st-weak{background:var(--bg);box-shadow:0 0 0 2px var(--ink)}
.here{background:transparent;border:1px solid var(--line)}
.kc-big::before{display:none}
.sync i,.sync.cloud i,.sync.local i{background:var(--ink-3)}
.hint-card{border-color:var(--line)}
.modal,.sheet{border:1px solid var(--line)}
.btn.danger{background:var(--surface)}
.ver{font-size:12px;color:var(--ink-3);font-family:var(--f-mono)}
.wtools{position:sticky;top:-18px;z-index:2;background:var(--bg);display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:10px 0;border-bottom:1px solid var(--line-2);margin-bottom:6px}
.wsel-n{font-weight:600;font-size:15px}
.wtools .btn.big{min-height:50px;font-size:16px}
.ck{display:inline-block;width:22px;height:22px;border:1.5px solid var(--ink-3);border-radius:5px;position:relative;vertical-align:middle}
.pk.on{background:var(--surface-2)}
.pk.on .ck{background:var(--ink);border-color:var(--ink)}
.pk.on .ck::after{content:"";position:absolute;left:6px;top:2px;width:6px;height:11px;border:solid var(--bg);border-width:0 2px 2px 0;transform:rotate(45deg)}
"""
rep('</style>\n</head>', MINIMAL + '</style>\n</head>')

# ======================================================================
# 10/5 저녁: 순서 항상 랜덤(이전 단어와 새 단어 고르게) · 카드 문장 먼저 + 문장 속 단어 뜻 · QA 수정
# ======================================================================
# --- 순서 ---
rep("  if (fresh || !ch.cur) { ch.cur = newRun(CHAPTERS[i].ids, S.shuf); ch.u = now; saveH(); }",
    "  if (fresh || !ch.cur) { ch.cur = newRun(mixIds(CHAPTERS[i]), false); ch.u = now; saveH(); }")
rep("function openChapter(i, fresh) {",
    "/* 새로 시작할 때마다 랜덤. 누적 장(1–100 등)은 앞 장 단어와 새로 추가된 단어를 고르게 섞음 */\n"
    "function mixIds(c) {\n"
    "  const ids = c.ids;\n"
    "  if (c.kind !== 'step' || ids.length <= 50) return shuffled(ids);\n"
    "  const nN = ids.length - 50 * Math.floor((ids.length - 1) / 50);\n"
    "  const old = shuffled(ids.slice(0, ids.length - nN)), nw = shuffled(ids.slice(ids.length - nN));\n"
    "  const out = []; let i = 0, j = 0;\n"
    "  while (i < old.length || j < nw.length) {\n"
    "    if (j < nw.length && (i >= old.length || (j + 0.5) / nw.length <= (i + 0.5) / old.length)) out.push(nw[j++]); else out.push(old[i++]);\n"
    "  }\n"
    "  return out;\n"
    "}\n"
    "function openChapter(i, fresh) {")
rep("    '<div class=\"dlg-acts\"><button class=\"btn primary\" data-act=\"loopGo\" data-v=\"1\">섞어서 시작</button><button class=\"btn\" data-act=\"loopGo\" data-v=\"0\">순서대로</button></div>' +",
    "    '<div class=\"dlg-acts\"><button class=\"btn primary\" data-act=\"loopGo\" data-v=\"1\">시작 (순서 섞음)</button></div>' +")
rep("이제 모르는 단어를 다 맞힐 때까지 반복해요. 순서를 섞을까요?</p>'", "이제 모르는 단어를 다 맞힐 때까지 반복해요.</p>'")
rep(" + segB('setShuf', S.shuf, [[false, '번호 순서대로'], [true, '섞어서']]) +", " +")
rep("        '<p class=\"hint\">순서 설정은 새로 시작하는 회독부터 적용돼요. 장 끝의 ‘모르는 단어’ 반복은 매번 섞을지 물어봐요.</p></section>' +",
    "        '<p class=\"hint\">회독 순서는 새로 시작할 때마다 랜덤이에요. 누적 장은 앞 장 단어와 새 단어를 고르게 섞어요. 진행 중인 회독은 순서가 그대로예요.</p></section>' +")
# --- 카드 문장 먼저 + 단어 뜻 ---
_a = s.index('function sentHTML(w) {')
_b = s.index('/* 이 단어에서의 읽기가 음독인지 훈독인지')
s = s[:_a] + r"""const glossHTML = e => e.g && e.g.length ? '<p class="gl" data-act="peek"><span class="gl-l">단어</span>' + e.g.map(([a, b]) => '<span><b lang="ja">' + esc(a) + '</b>' + esc(b) + '</span>').join('') + '</p>' : '';
function sentHTML(w, first) {
  const idx = w.e.map((e, i) => i);
  if (first != null && first >= 0 && first < w.e.length) { idx.splice(first, 1); idx.unshift(first); }
  return '<section class="s-sent"><h3 class="sec-h"><span>BJT 예문</span><i class="rule"></i><span class="aux">' + w.e.length + '</span></h3>' +
    idx.map(i => {
      const e = w.e[i], sc = SCENE[e.s] || ['', e.s];
      return '<article class="sent' + (i === first ? ' card-s' : '') + '" data-i="' + i + '"><div class="sent-h"><span class="scene"><b>' + sc[0] + '</b>' + esc(sc[1]) + (i === first ? '<em class="card-l">카드 문장</em>' : '') + '</span>' +
        (CAN_SPEAK() ? '<button class="spk" data-act="sayS" data-id="' + w.id + '" data-i="' + i + '" aria-label="예문 듣기">' + ICON.spk + '</button>' : '') + '</div>' +
        '<p class="jp" lang="ja" data-act="peek">' + ruby(e.j) + '</p><p class="ko" data-act="peek">' + esc(e.k) + '</p>' + glossHTML(e) + '</article>';
    }).join('') + '</section>';
}
""" + s[_b:]
rep("'</div><div class=\"ex-b\">' + sentHTML(w) + '</div></div>';",
    "'</div><div class=\"ex-b\">' + sentHTML(w, !inSheet && ctx && view === 'study' && w.id === ui.id ? frontSentIdx(w, getRun()) : -1) + '</div></div>';")
rep("          '<p class=\"jp\" lang=\"ja\" data-act=\"peek\">' + ruby(e.j) + '</p><p class=\"ko\" data-act=\"peek\">' + esc(e.k) + '</p></article></section>' : '') +",
    "          '<p class=\"jp\" lang=\"ja\" data-act=\"peek\">' + ruby(e.j) + '</p><p class=\"ko\" data-act=\"peek\">' + esc(e.k) + '</p>' + glossHTML(e) + '</article></section>' : '') +")
# --- QA 수정 ---
# 1) 전체 초기화 뒤에도 백업 코드로 되살리기
rep("  const before = JSON.stringify(H);\n  mergeH(o.h);\n  if (o.s) mergeS(o.s);",
    "  const before = JSON.stringify(H);\n  if (o.h && typeof o.h === 'object' && nn(o.h.rs) < nn(H.rs)) o.h.rs = H.rs;   /* 직접 가져오기는 초기화보다 우선 */\n  mergeH(o.h);\n  if (o.s) mergeS(o.s);\n  applyJf();")
# 2) 설정을 바꿔도 스크롤 위치 유지
rep("function openSettings() {\n  sheetStack = [];",
    "function openSettings() { const sb = $('#sheet-body'), tt = $('#sheet-title'); const keep = sheetOpen && sb && tt && tt.textContent === '설정' ? sb.scrollTop : 0; openSettings0(); if (keep) { const b = $('#sheet-body'); if (b) b.scrollTop = keep; } }\nfunction openSettings0() {\n  sheetStack = [];")
# 5) 홈에서 되돌리기 해도 약점 개수 갱신
rep("toast(w.w + ' 삭제함', '되돌리기', () => { const p = JSON.parse(prev); if (p) { const x = cleanW(p); x.u = Date.now(); H.w[idAttr] = x; saveH(); } if (view === 'weak') renderWeak(); });",
    "toast(w.w + ' 삭제함', '되돌리기', () => { const p = JSON.parse(prev); if (p) { const x = cleanW(p); x.u = Date.now(); H.w[idAttr] = x; saveH(); } if (view === 'weak') renderWeak(); else if (view === 'home') renderHome(); });")
# 7) 해설에서 누른 ★는 이전(되돌리기)해도 유지
rep("  const w = s.w ? cleanW(JSON.parse(s.w)) : {n: 0, m: 0, l: -1, t: 0, pin: 0, rm: -1, u: 0};\n  w.u = now; H.w[s.id] = w;",
    "  const w = s.w ? cleanW(JSON.parse(s.w)) : {n: 0, m: 0, l: -1, t: 0, pin: 0, rm: -1, u: 0};\n  const cur = H.w[s.id]; if (cur) { w.pin = cur.pin; w.rm = cur.pin ? -1 : (cur.rm >= 0 ? Math.min(cur.rm, w.m) : w.rm); }\n  w.u = now; H.w[s.id] = w;")
MORE_CSS = """
.gl{display:flex;flex-wrap:wrap;align-items:baseline;gap:3px 14px;margin-top:8px;font-size:14px;line-height:1.55;color:var(--ink-2)}
.gl b{font-weight:500;color:var(--ink);margin-right:5px;font-family:var(--f-jp);font-size:15px}
.gl-l{font-size:11px;letter-spacing:.1em;color:var(--ink-3);margin-right:2px}
.tr-off .sent:not(.peek) .gl{color:transparent;background:var(--mask);border-radius:4px;-webkit-user-select:none;user-select:none}
.tr-off .sent:not(.peek) .gl b,.tr-off .sent:not(.peek) .gl-l{color:transparent}
.card-l{font-style:normal;font-size:12px;font-weight:600;color:var(--ink);border:1px solid var(--ink);border-radius:4px;padding:1px 6px;margin-left:6px}
.sent.card-s{border-top:0}
[data-act]{cursor:pointer}
.wtools{top:0}
.ribbon{display:none}
@media (max-width:620px){.book{aspect-ratio:auto;min-height:172px}.bbody{padding-bottom:52px}}
"""
rep('</style>\n</head>', MORE_CSS + '</style>\n</head>')

# ================= 10/5 22:20 요청 =================
# 1) 약점 기준: 기본 5번(장을 넘나들며 누적), 선택지 3·5·7. 예전 2·3번 설정은 5번으로 한 번 옮김
rep("const DEF = {auto: true, rate: 1, sent: true, shuf: false, wkN: 2, furi: 'all', tr: 'show', kp: false, lis: false, jf: 'm', exam: DEF_EXAM, em: 0, u: 0};",
    "const DEF = {auto: true, rate: 1, sent: true, shuf: false, wkN: 5, wv: 2, furi: 'all', tr: 'show', kp: false, lis: false, jf: 'm', exam: DEF_EXAM, em: 0, u: 0};")
rep("  if (+o.wkN === 2 || +o.wkN === 3) r.wkN = +o.wkN;",
    "  if (o.wv === 2 && [3, 5, 7].includes(+o.wkN)) r.wkN = +o.wkN;   /* 예전 2·3번 설정은 버리고 5번 */")
rep("      '<section><h3>약점 자동 추가</h3>' + segB('setWk', S.wkN, [[2, '2번 모르면'], [3, '3번 모르면']]) + '</section>' +",
    "      '<section><h3>약점 자동 추가</h3>' + segB('setWk', S.wkN, [[3, '3번'], [5, '5번'], [7, '7번']]) + '<p class=\"hint\">‘모르겠음’ 누른 횟수를 장을 넘나들며 합쳐요. 예: 1–50에서 3번 + 1–100에서 2번 = 5번 → 약점 단어로.</p></section>' +")
rep("segB('setAuto', S.auto, [[true, '해설·1회독에서 자동 발음'], [false, '누를 때만']])",
    "segB('setAuto', S.auto, [[true, '해설에서 자동 발음'], [false, '누를 때만']])")

# 2) 약점 카드 복습: 많이 틀린 단어부터(같은 횟수끼리는 섞음)
rep("function openWeak(fresh) {",
    "function weakOrder(ids) {\n  const g = new Map();\n  for (const id of ids) { const m = H.w[id] ? H.w[id].m : 0; if (!g.has(m)) g.set(m, []); g.get(m).push(id); }\n  return [...g.keys()].sort((a, b) => b - a).flatMap(m => shuffled(g.get(m)));\n}\nfunction openWeak(fresh) {")
rep("    H.wr = newRun(shuffled(ids), false); H.wru = now; saveH();",
    "    H.wr = newRun(weakOrder(ids), false); H.wru = now; saveH();")
rep("  const sub = ctx.kind === 'ch' ? 'No.' + CHAPTERS[ctx.i].a + '–' + CHAPTERS[ctx.i].b : (r ? r.ord.length + '개 섞어서' : '약점 단어');",
    "  const sub = ctx.kind === 'ch' ? 'No.' + CHAPTERS[ctx.i].a + '–' + CHAPTERS[ctx.i].b : (r ? r.ord.length + '개 · 많이 틀린 순' : '약점 단어');")
rep("'>처음부터 (' + ids.length + '개 섞어서)</button>'",
    "'>처음부터 (' + ids.length + '개 · 많이 틀린 순)</button>'")
rep("'>카드로 복습 · ' + ids.length + '개 섞어서</button>'",
    "'>카드로 복습 · ' + ids.length + '개 (많이 틀린 순)</button>'")
rep("'<p class=\"note\" style=\"margin:4px 0 12px\">' + S.wkN + '번 이상 ‘모르겠음’ 누른 단어와 ★로 넣은 단어가 모여요. 많이 틀린 순.",
    "'<p class=\"note\" style=\"margin:4px 0 12px\">장을 넘나들며 합쳐서 ' + S.wkN + '번 이상 ‘모르겠음’ 누른 단어와 ★로 넣은 단어가 모여요. 많이 틀린 순이고, 카드 복습도 이 순서예요.")

# 3) 모르는 단어 다시보기: 첫 라운드와 그 뒤 모든 라운드에서 ‘순서 섞을까요?’
rep("  if (id == null && r.ph === 'loop' && r.next.length) { startNextRound(r); id = curId(r); }",
    "  if (id == null && r.ph === 'loop' && r.next.length) { renderRoundDialog(r); return; }")
rep("  toast(r.q.length + '개 남음 · ' + r.round + '라운드');",
    "  toast(r.round + '라운드 · ' + r.q.length + '개 · ' + (r.shuf ? '섞어서' : '순서대로'));")
rep("    '<div class=\"dlg-acts\"><button class=\"btn primary\" data-act=\"loopGo\" data-v=\"1\">시작 (순서 섞음)</button></div>' +\n    (undoStack.length ? '<button class=\"link\" data-act=\"undo\">마지막 답 되돌리기</button>' : '') + '</div>', false);\n}",
    "    '<p class=\"q\">순서를 섞을까요?</p>' +\n    '<div class=\"dlg-acts\"><button class=\"btn primary\" data-act=\"loopGo\" data-v=\"1\">섞어서</button><button class=\"btn\" data-act=\"loopGo\" data-v=\"0\">순서대로</button></div>' +\n    (undoStack.length ? '<button class=\"link\" data-act=\"undo\">마지막 답 되돌리기</button>' : '') + '</div>', false);\n}\n"
    "function renderRoundDialog(r) {\n  V.study.innerHTML = sbarHTML(r, null) + '<div class=\"scroll\"><div class=\"stage\"></div></div>';\n"
    "  openModal('<div class=\"dlg\"><div class=\"hanko\" aria-hidden=\"true\">復</div><h2>아직 모르는 단어 ' + r.next.length + '개</h2>' +\n"
    "    '<p>' + r.round + '라운드 끝. ' + (r.round + 1) + '라운드로 한 번 더 봐요.</p><p class=\"q\">순서를 섞을까요?</p>' +\n"
    "    '<div class=\"dlg-acts\"><button class=\"btn primary\" data-act=\"roundGo\" data-v=\"1\">섞어서</button><button class=\"btn\" data-act=\"roundGo\" data-v=\"0\">순서대로</button></div>' +\n"
    "    (undoStack.length ? '<button class=\"link\" data-act=\"undo\">마지막 답 되돌리기</button>' : '') + '</div>', false);\n}\n"
    "function roundGo(shuf) {\n  const r = getRun();\n  if (!r || r.ph !== 'loop' || curId(r) != null || !r.next.length) { enterCard(); return; }\n  r.shuf = shuf; startNextRound(r); enterCard();\n}")
rep("    case 'loopGo': loopGo(el.dataset.v === '1'); break;",
    "    case 'loopGo': loopGo(el.dataset.v === '1'); break;\n    case 'roundGo': roundGo(el.dataset.v === '1'); break;")

# 4) 홈: 가볍게 1회독 삭제, 그 자리(맨 위)에 약점 단어
rep("installHint() + liteHTML() + banner + partsHTML()", "installHint() + weakTopHTML() + banner + partsHTML()")
rep("'<section class=\"grp\"><div class=\"zrow\"><div class=\"side\"><button class=\"btn big\" data-act=\"weakView\"><span>★ 약점 단어</span><small>' + wk + '개</small></button>' +\n        '<button class=\"btn big\" data-act=\"browse\">",
    "'<section class=\"grp\"><div class=\"zrow\"><div class=\"side\"><button class=\"btn big\" data-act=\"browse\">")
rep("        '<li><b>가볍게 1회독</b>: 처음 보는 단어를 부수 → 한자 → 단어 이야기와 함께 한 번씩 훑어요. 반복 없음. 먼저 이걸로 전체를 한 번 보세요.</li>' +\n", "")
rep("        '<li>' + S.wkN + '번 이상 모르겠음 누른 단어는 <b>약점 단어</b>에 자동으로 모여요. ★로 직접 넣고 뺄 수도 있어요.</li>' +",
    "        '<li>장을 넘나들며 합쳐서 ' + S.wkN + '번 이상 모르겠음 누른 단어는 맨 위 <b>약점 단어</b>에 자동으로 모여요(많이 틀린 순). ★로 직접 넣고 뺄 수도 있어요.</li>' +")
rep("function liteHTML() {",
    "function weakTopHTML() {\n  const ids = weakIds(), n = ids.length, wr = H.wr;\n"
    "  const top = ids.slice(0, 4).map(id => '<span><b lang=\"ja\">' + esc(byId.get(id).w) + '</b>' + (H.w[id].m ? '×' + H.w[id].m : '★') + '</span>').join('');\n"
    "  const go = wr ? '<button class=\"btn primary big\" data-act=\"weakGo\">약점 복습 이어서 · ' + progText(wr) + '</button>'\n"
    "    : '<button class=\"btn primary big\" data-act=\"weakNew\"' + (n ? '' : ' disabled') + '>약점 카드 복습 · 많이 틀린 순</button>';\n"
    "  return '<section class=\"wk-top\"><div class=\"wk-h\"><b>★ 약점 단어 ' + n + '개</b><span>' + (n ? top : '합쳐서 ' + S.wkN + '번 모르면 여기로 모여요') + '</span></div>' +\n"
    "    '<div class=\"wk-acts\">' + go + '<button class=\"btn big\" data-act=\"weakView\">목록 보기</button></div></section>';\n}\n"
    "function liteHTML() {")

# 5) 해설: 뜻 바로 아래 암기 한 줄 + 중요한 곳 밑줄(결론 →, 「」 표현)
rep("const mixJa = t => esc(t).replace(JA_RUN, m => '<span lang=\"ja\">' + m + '</span>');",
    "const mixJa = t => esc(t).replace(JA_RUN, m => '<span lang=\"ja\">' + m + '</span>');\n"
    "/* 밑줄 강조: 괄호 밖 마지막 → 뒤의 결론, BJT 포인트의 「」 표현 */\n"
    "function lastTopArrow(t) { let d = 0, at = -1; for (let i = 0; i < t.length; i++) { const c = t[i]; if (c === '(' || c === '（') d++; else if ((c === ')' || c === '）') && d) d--; else if (c === '→' && !d) at = i; } return at; }\n"
    "function emArrow(t, stopParen) {\n  t = String(t || ''); const a = lastTopArrow(t); if (a < 0) return mixJa(t);\n  let s = a + 1; while (t[s] === ' ') s++;\n"
    "  const re = stopParen ? /\\(|（|\\.\\s|\\.$/g : /\\.\\s|\\.$/g; re.lastIndex = s; const m = re.exec(t); const e = m ? m.index : t.length;\n"
    "  if (e <= s) return mixJa(t);\n  return mixJa(t.slice(0, s)) + '<u class=\"em\">' + mixJa(t.slice(s, e)) + '</u>' + mixJa(t.slice(e));\n}\n"
    "const emQuote = t => String(t || '').split(/(「[^」]*」)/).map((p, i) => i % 2 ? '<u class=\"em\">' + mixJa(p) + '</u>' : mixJa(p)).join('');\n"
    "const mnHTML = t => mixJa(t).replace('(소리 연상)', '<small class=\"mn-s\">소리 연상</small>');")
rep("    '<div class=\"ans-mean\">' + mixJa(w.m) + '</div>' +\n    (sub.length",
    "    '<div class=\"ans-mean\">' + mixJa(w.m) + '</div>' +\n    (w.mn ? '<p class=\"ans-mn\"><span class=\"mn-l\">암기</span>' + mnHTML(w.mn) + '</p>' : '') +\n    (sub.length")
rep("      (k.x ? '<p class=\"lk-x\">' + mixJa(k.x) + '</p>' : '') + '</div></div>';",
    "      (k.x ? '<p class=\"lk-x\">' + emArrow(k.x, true) + '</p>' : '') + '</div></div>';")
rep("  const st = w.st ? '<p class=\"st-w\">' + mixJa(w.st) + '</p>' : '';",
    "  const st = w.st ? '<p class=\"st-w\">' + emArrow(w.st, false) + '</p>' : '';")
rep("const ptHTML = w => w.p ? '<section class=\"s-pt pt\"><span class=\"pt-l\">BJT 포인트</span><p>' + mixJa(w.p) + '</p></section>' : '';",
    "const ptHTML = w => w.p ? '<section class=\"s-pt pt\"><span class=\"pt-l\">BJT 포인트</span><p>' + emQuote(w.p) + '</p></section>' : '';")
rep("      '<p class=\"kx\">' + mixJa(k.x) + '</p>' +",
    "      '<p class=\"kx\">' + emArrow(k.x, true) + '</p>' +")

CSS_1022 = """
.wk-top{width:100%;display:flex;flex-direction:column;gap:10px;border:1px solid var(--line);border-radius:14px;background:var(--surface);padding:14px 16px}
.wk-h{display:flex;align-items:baseline;gap:6px 14px;flex-wrap:wrap}
.wk-h b{font-size:clamp(18px,2.2vw,22px);font-weight:700}
.wk-h span{font-size:14px;color:var(--ink-2);display:flex;flex-wrap:wrap;gap:4px 12px}
.wk-h span b{font-size:15px;font-weight:500;color:var(--ink);margin-right:2px}
.wk-acts{display:flex;gap:10px;flex-wrap:wrap}
.wk-acts .btn{flex:1 1 180px}
.wk-acts .btn.primary{flex:2 1 240px}
u.em{text-decoration:underline;text-decoration-thickness:1.5px;text-underline-offset:3px;text-decoration-skip-ink:none;font-weight:600;color:var(--ink)}
.ans-mn{margin-top:10px;padding:6px 0 6px 12px;border-left:3px solid var(--ink);font-size:clamp(16px,1.8vw,19px);line-height:1.55;color:var(--ink);text-align:left}
.mn-l{font-size:11px;letter-spacing:.12em;font-weight:600;color:var(--ink-3);margin-right:8px;vertical-align:1px}
.mn-s{font-size:12px;color:var(--ink-3);margin-left:4px;white-space:nowrap}
.dlg p.q{font-size:18px;font-weight:700;color:var(--ink);margin-top:2px}
"""
rep('</style>\n</head>', CSS_1022 + '</style>\n</head>')
# 시험용 창구(앱 동작에는 영향 없음)
rep("  try { if (navigator.storage && navigator.storage.persisted) navigator.storage.persisted().then(p => { if (!p && navigator.storage.persist) return navigator.storage.persist(); }).catch(() => {}); } catch (e) {}\n}\n})();",
    "  try { if (navigator.storage && navigator.storage.persisted) navigator.storage.persisted().then(p => { if (!p && navigator.storage.persist) return navigator.storage.persist(); }).catch(() => {}); } catch (e) {}\n}\nwindow.__t = {get ui() { return ui; }, getRun, isWeak, get S() { return S; }, get H() { return H; }};\n})();")

# ================= 10/7 요청 =================
# 1) 시험일 10/13(화)로: 기본값 + 예전 기본값(10/7·10/8)이면 한 번만 옮김
rep("const DEF_EXAM = '2026-10-08';", "const DEF_EXAM = '2026-10-13';")
rep("  if (o.em === 1) r.em = 1;", "  if (o.em === 1 || o.em === 2) r.em = o.em;")
rep("if (!S.em) { if (S.exam === '2026-10-07') S.exam = '2026-10-08'; S.em = 1; LS.set(KS, S); }",
    "if (!(S.em >= 2)) { if (S.exam === '2026-10-07' || S.exam === '2026-10-08') S.exam = '2026-10-13'; S.em = 2; LS.set(KS, S); }")
# 2) 암기 한 줄 삭제 → 그 자리에 '같은 한자' 단어(크게, 후리가나·뜻, 누르면 열림)
rep("    (w.mn ? '<p class=\"ans-mn\"><span class=\"mn-l\">암기</span>' + mnHTML(w.mn) + '</p>' : '') +\n",
    "    skHTML(w) +\n")
rep("function ansHTML(w, inSheet) {",
    "/* 같은 한자를 쓰는 다른 단어: 한자마다 6개(본 단어 먼저, 그다음 번호순), 나머지는 +N. 지금 단어·이미 나온 단어는 빼기 */\n"
    "const SK_N = 6;\n"
    "const shortM = m => { let t = String(m || '').replace(/\\([^)]*\\)/g, '').replace(/\\s+/g, ' ').trim(); if (!t) t = String(m || ''); return t.length > 16 ? t.slice(0, 15) + '…' : t; };\n"
    "function skHTML(w) {\n"
    "  const ks = [...new Set(w.kj || [])].filter(c => K[c]);\n"
    "  if (!ks.length) return '';\n"
    "  const shown = new Set([w.id]);\n"
    "  const seen = id => { const x = H.w[id]; return x && x.l !== -1 ? 1 : 0; };\n"
    "  const rows = ks.map(c => {\n"
    "    const ids = K[c].u.filter(id => byId.has(id) && !shown.has(id)).sort((a, b) => (seen(b) - seen(a)) || (NO.get(a) - NO.get(b)));\n"
    "    if (!ids.length) return '';\n"
    "    ids.slice(0, SK_N).forEach(id => shown.add(id));\n"
    "    const items = ids.map((id, i) => { const o = byId.get(id); return '<button class=\"sk-w' + (i >= SK_N ? ' more' : '') + '\" data-act=\"open\" data-id=\"' + id + '\"><span class=\"sk-j\" lang=\"ja\">' + headRuby(o) + '</span><span class=\"sk-m\">' + mixJa(shortM(o.m)) + '</span></button>'; }).join('');\n"
    "    return '<div class=\"sk-row\"><span class=\"sk-k\" lang=\"ja\">' + esc(c) + '</span><div class=\"sk-ws\">' + items + (ids.length > SK_N ? '<button class=\"sk-more\" data-act=\"skMore\">+' + (ids.length - SK_N) + '개 더</button>' : '') + '</div></div>';\n"
    "  }).join('');\n"
    "  return rows ? '<section class=\"sk\"><span class=\"sk-l\">같은 한자</span>' + rows + '</section>' : '';\n"
    "}\n"
    "function ansHTML(w, inSheet) {")
rep("    case 'open': openWord(+el.dataset.id); break;",
    "    case 'open': openWord(+el.dataset.id); break;\n    case 'skMore': { const row = el.closest('.sk-row'); if (row) row.classList.add('open'); break; }")
CSS_1007 = """
.sk{display:flex;flex-direction:column;gap:10px;margin-top:14px;text-align:left}
.sk-l{font-family:var(--f-mono);font-size:11px;letter-spacing:.12em;color:var(--ink-3)}
.sk-row{display:grid;grid-template-columns:46px minmax(0,1fr);gap:10px;align-items:start}
.sk-k{width:46px;height:46px;border:1px solid var(--line);border-radius:6px;display:grid;place-items:center;font-family:var(--f-kyo);font-weight:500;font-size:32px;line-height:1;background:var(--bg)}
.sk-ws{display:flex;flex-wrap:wrap;gap:8px;min-width:0}
.sk-w{display:flex;flex-direction:column;align-items:flex-start;justify-content:flex-end;gap:2px;padding:4px 10px 6px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--ink);text-align:left;max-width:100%}
.sk-j{font-family:var(--f-kyo);font-weight:500;font-size:32px;line-height:1.1;padding-top:14px;white-space:nowrap}
.sk-j rt{font-family:var(--f-jp);font-weight:400;font-size:13px;line-height:1;color:var(--ink-2);letter-spacing:0}
.sk-m{font-size:13px;line-height:1.3;color:var(--ink-2);max-width:12em}
.sk-w.more{display:none}
.sk-row.open .sk-w.more{display:flex}
.sk-row.open .sk-more{display:none}
.sk-more{align-self:stretch;min-height:44px;padding:0 12px;border:1px dashed var(--line);border-radius:8px;background:transparent;font-size:14px;color:var(--ink-2)}
"""
rep('</style>\n</head>', CSS_1007 + '</style>\n</head>')
# 3) (15:59 추가) 한자·부수 풀이는 예문 아래로, 한자음·바꿔 말하면 줄은 뜻 바로 아래로, 같은 한자 네모 칸 밑에 훈음
rep("  return '<div class=\"ex\"><div class=\"ex-a\">' + ansHTML(w, inSheet) + storyHTML(w, 's-story') + ptHTML(w) + pairHTML(w) + kpHTML(w) + '</div><div class=\"ex-b\">' + sentHTML(w, !inSheet && ctx && view === 'study' && w.id === ui.id ? frontSentIdx(w, getRun()) : -1) + '</div></div>';",
    "  return '<div class=\"ex\"><div class=\"ex-a\">' + ansHTML(w, inSheet) + storyHTML(w, 's-story') + ptHTML(w) + pairHTML(w) + '</div><div class=\"ex-b\">' + sentHTML(w, !inSheet && ctx && view === 'study' && w.id === ui.id ? frontSentIdx(w, getRun()) : -1) + kpHTML(w) + '</div></div>';")
rep("    skHTML(w) +\n    (sub.length ? '<div class=\"ans-sub\">' + sub.join('') + '</div>' : '') +\n  '</section>';",
    "    (sub.length ? '<div class=\"ans-sub\">' + sub.join('') + '</div>' : '') +\n    skHTML(w) +\n  '</section>';")
rep("    return '<div class=\"sk-row\"><span class=\"sk-k\" lang=\"ja\">' + esc(c) + '</span><div class=\"sk-ws\">'",
    "    const kh = K[c].h ? K[c].h.replace(/^\\?\\s*/, '') : '';\n"
    "    return '<div class=\"sk-row\"><span class=\"sk-kc\"><span class=\"sk-k\" lang=\"ja\">' + esc(c) + '</span>' + (kh ? '<span class=\"sk-h\">' + esc(kh) + '</span>' : '') + '</span><div class=\"sk-ws\">'")
CSS_1007b = """
.sk-row{grid-template-columns:58px minmax(0,1fr)}
.sk-kc{display:flex;flex-direction:column;align-items:center;gap:4px;min-width:0}
.sk-h{font-size:11.5px;line-height:1.25;color:var(--ink-2);text-align:center;word-break:keep-all;overflow-wrap:anywhere;max-width:58px}
"""
rep('</style>\n</head>', CSS_1007b + '</style>\n</head>')
# 4) (16:08) 이야기를 뜻 바로 아래(원래 자리)로, 같은 한자는 이야기 아래로. 학습 화면에도 전체화면 버튼
rep("    (sub.length ? '<div class=\"ans-sub\">' + sub.join('') + '</div>' : '') +\n    skHTML(w) +\n  '</section>';",
    "    (sub.length ? '<div class=\"ans-sub\">' + sub.join('') + '</div>' : '') +\n  '</section>';")
rep("ansHTML(w, inSheet) + storyHTML(w, 's-story') + ptHTML(w) + pairHTML(w) + '</div><div class=\"ex-b\">'",
    "ansHTML(w, inSheet) + storyHTML(w, 's-story') + skHTML(w) + ptHTML(w) + pairHTML(w) + '</div><div class=\"ex-b\">'")
rep("    '<button class=\"tb\" data-act=\"undo\" aria-label=\"이전 카드로 되돌리기\"' + (undoStack.length ? '' : ' disabled') + '>' + ICON.undo + '<span class=\"sm-hide\">이전</span></button>' +\n  '</header>",
    "    '<button class=\"tb\" data-act=\"undo\" aria-label=\"이전 카드로 되돌리기\"' + (undoStack.length ? '' : ' disabled') + '>' + ICON.undo + '<span class=\"sm-hide\">이전</span></button>' +\n    (FS.ok && !STANDALONE ? '<button class=\"tb\" data-act=\"full\" aria-label=\"전체화면\">' + ICON.full + '<span class=\"sm-hide\">전체화면</span></button>' : '') +\n  '</header>")
rep('</style>\n</head>', '.sk{margin-top:0;order:2}\n@media (max-width:560px){.sbar [data-act="full"]{display:none}}\n</style>\n</head>')
OLD_FS_1007 = "const FS = {\n  ok: !!(document.fullscreenEnabled || document.webkitFullscreenEnabled),\n  on() { return !!(document.fullscreenElement || document.webkitFullscreenElement); },\n  toggle() {\n    try {\n      if (this.on()) { const f = document.exitFullscreen || document.webkitExitFullscreen; if (f) { const p = f.call(document); if (p && p.catch) p.catch(() => {}); } }\n      else {\n        const el = document.documentElement, f = el.requestFullscreen || el.webkitRequestFullscreen;\n        if (!f) throw new Error('no');\n        const p = f.call(el);\n        if (p && p.catch) p.catch(() => toast('이 화면에선 전체화면이 막혀 있어요. Safari에서 열어 보세요.'));\n      }\n    } catch (e) { toast('이 화면에선 전체화면이 막혀 있어요. Safari에서 열어 보세요.'); }\n  }\n};"
NEW_FS_1007 = '// 아이패드 Safari는 아래로 쓸어내리면 전체화면을 끈다(웹에서 막을 수 없음: WebKit 정책).\n// 그래서 전체화면 버튼으로 끈 게 아니면 \'켜 둔 상태\'를 기억했다가, 다음 탭에서 바로 다시 켠다.\nconst FS = {\n  ok: !!(document.fullscreenEnabled || document.webkitFullscreenEnabled),\n  want: (() => { try { return sessionStorage.getItem(\'bjt-fs\') === \'1\'; } catch (e) { return false; } })(),\n  busy: false,\n  setWant(v) { this.want = v; try { sessionStorage.setItem(\'bjt-fs\', v ? \'1\' : \'0\'); } catch (e) {} },\n  on() { return !!(document.fullscreenElement || document.webkitFullscreenElement); },\n  enter(quiet) {\n    const el = document.documentElement, f = el.requestFullscreen || el.webkitRequestFullscreen;\n    const fail = () => { this.busy = false; if (!quiet) { this.setWant(false); toast(\'이 화면에선 전체화면이 막혀 있어요. Safari에서 열어 보세요.\'); } };\n    if (!f) { fail(); return; }\n    this.busy = true;\n    let p;\n    try { p = f.call(el); } catch (e) { fail(); return; }\n    if (p && p.then) p.then(() => { this.busy = false; }, fail);\n    else setTimeout(() => { this.busy = false; }, 700);\n  },\n  toggle() {\n    if (this.on()) {\n      this.setWant(false);\n      const f = document.exitFullscreen || document.webkitExitFullscreen;\n      if (f) { try { const p = f.call(document); if (p && p.catch) p.catch(() => {}); } catch (e) {} }\n    } else { this.setWant(true); this.enter(false); }\n  },\n  restore(e) {\n    if (!this.ok || STANDALONE || !this.want || this.busy || this.on()) return;\n    const t = e && e.target;\n    if (t && t.closest && t.closest(\'[data-act="full"]\')) return;   // 버튼은 toggle()이 처리\n    this.enter(true);\n  }\n};\n(() => {\n  // 드래그(스크롤)가 아니라 \'탭\'일 때만 다시 켠다 — 스크롤 도중에 화면이 출렁이지 않게\n  let sx = 0, sy = 0, st = 0, multi = false;\n  document.addEventListener(\'touchstart\', e => {\n    multi = e.touches.length > 1;\n    const p = e.touches[0]; sx = p.clientX; sy = p.clientY; st = Date.now();\n  }, {capture: true, passive: true});\n  document.addEventListener(\'touchend\', e => {\n    if (multi || e.touches.length) return;\n    const p = e.changedTouches[0]; if (!p) return;\n    if (Math.abs(p.clientX - sx) > 12 || Math.abs(p.clientY - sy) > 12 || Date.now() - st > 600) return;\n    FS.restore(e);\n  }, {capture: true, passive: true});\n  document.addEventListener(\'click\', e => FS.restore(e), true);\n})();'
# 5) (10/7 17:33) 전체화면은 전체화면 버튼으로만 끄기: 쓸어내려서 꺼지면 다음 탭에서 자동으로 다시 켬
rep(OLD_FS_1007, NEW_FS_1007)

# ================= 10/13 요청: 0부 · 기본 (N5·N4 기초 단어) + 시험일 10/22 =================
# 1) 순서: 1500 단어(ORDER)는 그대로, 기본 카드(bn)는 따로 BORDER. 1500과 겹치는 기본 카드는 같은 카드를 씀
rep("const ORDER = W.slice().sort((a, b) => a.ord - b.ord).map(w => w.id);",
    "const ORDER = W.filter(w => w.ord != null).sort((a, b) => a.ord - b.ord).map(w => w.id);")
rep("const TOTAL = ORDER.length;\n",
    "const TOTAL = ORDER.length;\n"
    "/* 0부 기본: 기본 번호(bn) 순서. 1500 단어와 겹치는 카드는 같은 카드(기록도 같이 쌓임) */\n"
    "const BORDER = W.filter(w => w.bn != null).sort((a, b) => a.bn - b.bn).map(w => w.id);\n"
    "const BNO = new Map(BORDER.map(id => [id, byId.get(id).bn]));\n"
    "const BTOTAL = BORDER.length;\n"
    "const ALL_IDS = ORDER.concat(BORDER.filter(id => !NO.has(id)));\n"
    "const ALLN = ALL_IDS.length;\n"
    "const numLabel = id => NO.has(id) ? 'No.' + NO.get(id) + (BNO.has(id) ? ' · 기본 ' + BNO.get(id) : '') : '기본 ' + BNO.get(id);\n"
    "const rowNum = id => NO.has(id) ? NO.get(id) : '기' + BNO.get(id);\n"
    "const sortNo = id => NO.has(id) ? NO.get(id) : TOTAL + (BNO.get(id) || 0);\n")
# 2) 장: 기본 장은 1500 장 뒤에 붙임(번호·기록 그대로). 장 지문은 장마다 단어 구성으로 → 기본 단어를 뒤에 더 올려도 앞 장 진도 유지
rep("const KEY2I = new Map(CHAPTERS.map(c => [c.key, c.i]));",
    "const BCH0 = CHAPTERS.length;\n"
    "(() => {\n"
    "  const hs = ids => { let h = 2166136261; for (const id of ids) { h ^= id; h = Math.imul(h, 16777619) >>> 0; } return h.toString(36) + '.' + ids.length; };\n"
    "  genChapters(BTOTAL).forEach(c => { const ids = BORDER.slice(c.a - 1, c.b); CHAPTERS.push(Object.assign(c, {i: CHAPTERS.length, ids, cnt: ids.length, basic: true, key: 'B:' + hs(ids) + ':' + c.a + '-' + c.b + ':' + c.kind})); });\n"
    "})();\n"
    "const KEY2I = new Map(CHAPTERS.map(c => [c.key, c.i]));")
rep("const chName = i => '第' + (i + 1) + '章';",
    "const chName = i => CHAPTERS[i] && CHAPTERS[i].basic ? '基本' + (i - BCH0 + 1) + '章' : '第' + (i + 1) + '章';\n"
    "const chRange = c => (c.basic ? '기본 ' : 'No.') + c.a + '–' + c.b;")
rep("aria-label=\"' + chName(c.i) + ' ' + (ch.n + 1) + '회독 No.' + c.a + '–' + c.b + '\">'",
    "aria-label=\"' + chName(c.i) + ' ' + (ch.n + 1) + '회독 ' + chRange(c) + '\">'")
rep("'<span class=\"b-range\">No.' + c.a + '–' + c.b + '</span>'", "'<span class=\"b-range\">' + chRange(c) + '</span>'")
rep("'회독 · No.' + c.a + '–' + c.b + ' · ' + c.cnt + '단어</span></span><span class=\"r-go\">시작 →</span></button>';",
    "'회독 · ' + chRange(c) + ' · ' + c.cnt + '단어</span></span><span class=\"r-go\">시작 →</span></button>';")
rep("const sub = ctx.kind === 'ch' ? 'No.' + CHAPTERS[ctx.i].a + '–' + CHAPTERS[ctx.i].b :", "const sub = ctx.kind === 'ch' ? chRange(CHAPTERS[ctx.i]) :")
rep("rows = '<dt>장</dt><dd>' + chName(info.i) + ' · No.' + c.a + '–' + c.b + '</dd>", "rows = '<dt>장</dt><dd>' + chName(info.i) + ' · ' + chRange(c) + '</dd>")
rep("    const nx = CHAPTERS[info.i + 1];\n", "    const nx0 = CHAPTERS[info.i + 1], nx = nx0 && !!nx0.basic === !!c.basic ? nx0 : null;\n")
rep("if (c.kind === 'all') guide = TOTAL + '개 전체 회독 완료.", "if (c.kind === 'all') guide = (c.basic ? '기본 ' + BTOTAL : TOTAL) + '개 전체 회독 완료.")
rep("guide = 'No.' + c.a + '–' + c.b + ' 총정리 완료. ' + (nx ? '다음은 ' + chName(nx.i) + '(No.' + nx.a + '–' + nx.b + ').' : '');",
    "guide = chRange(c) + ' 총정리 완료. ' + (nx ? '다음은 ' + chName(nx.i) + '(' + chRange(nx) + ').' : '');")
rep("guide = 'No.' + c.a + '–' + c.b + ' 묶음 완성.", "guide = chRange(c) + ' 묶음 완성.")
rep("openSheet(chName(i) + ' · No.' + c.a + '–' + c.b,", "openSheet(chName(i) + ' · ' + chRange(c),")
# 3) 카드 번호 표시: 1500 단어 No.X, 기본 전용 카드는 '기본 N', 겹치는 카드는 둘 다
rep("<span class=\"no\">No.' + NO.get(w.id) + '</span>'", "<span class=\"no\">' + numLabel(w.id) + '</span>'", 3)
rep("(pick ? '<i class=\"ck\"></i>' : NO.get(id))", "(pick ? '<i class=\"ck\"></i>' : rowNum(id))")
rep("const tierTag = t => '<b class=\"tb-t' + (t === 'S' ? ' t-S' : '') + '\" title=\"' + t + '급\">' + t + '</b>';",
    "const tierTag = t => t === 'K' ? '<b class=\"tb-t t-K\" title=\"기본 단어\">기본</b>' : '<b class=\"tb-t' + (t === 'S' ? ' t-S' : '') + '\" title=\"' + t + '급\">' + t + '</b>';")
# 4) 약점·목록·음성 받기: 기본 카드 포함
rep("const weakIds = () => ORDER.filter(isWeak).sort((a, b) => (H.w[b].m - H.w[a].m) || (NO.get(a) - NO.get(b)));",
    "const weakIds = () => ALL_IDS.filter(isWeak).sort((a, b) => (H.w[b].m - H.w[a].m) || (sortNo(a) - sortNo(b)));")
rep("  for (const id of ORDER) {\n    const w = byId.get(id);\n    if (B.tier !== 'all' && w.t !== B.tier) continue;",
    "  for (const id of ALL_IDS) {\n    const w = byId.get(id);\n    if (B.tier !== 'all' && (B.tier === 'K' ? !BNO.has(id) : w.t !== B.tier)) continue;")
rep("seg('tier', [['all', '전체'], ['S', 'S'], ['A', 'A'], ['B', 'B']])", "seg('tier', [['all', '전체'], ['S', 'S'], ['A', 'A'], ['B', 'B']].concat(BTOTAL ? [['K', '기본']] : []))")
rep("function audioUrls() { const out = []; for (const id of ORDER) {", "function audioUrls() { const out = []; for (const id of ALL_IDS) {")
# 5) 같은 한자: 기본 단어 2개(기본 번호순)를 먼저 → 1500 단어(본 것 먼저, 번호순) → 나머지 기본 단어는 '+N개 더' 뒤로
rep("const SK_N = 6;\n",
    "const SK_N = 6;\n"
    "function relIds(c, skip) {\n"
    "  const ids = K[c].u.filter(id => byId.has(id) && !skip.has(id));\n"
    "  const seen = id => { const x = H.w[id]; return x && x.l !== -1 ? 1 : 0; };\n"
    "  const anchor = ids.filter(id => BNO.has(id)).sort((a, b) => BNO.get(a) - BNO.get(b)).slice(0, 2), an = new Set(anchor);\n"
    "  const main = ids.filter(id => NO.has(id) && !an.has(id)).sort((a, b) => (seen(b) - seen(a)) || (NO.get(a) - NO.get(b)));\n"
    "  const rest = ids.filter(id => !NO.has(id) && !an.has(id)).sort((a, b) => (seen(b) - seen(a)) || (BNO.get(a) - BNO.get(b)));\n"
    "  return anchor.concat(main, rest);\n"
    "}\n")
rep("    const ids = K[c].u.filter(id => byId.has(id) && !shown.has(id)).sort((a, b) => (seen(b) - seen(a)) || (NO.get(a) - NO.get(b)));",
    "    const ids = relIds(c, shown);")
rep("    const rel = k.u.filter(id => id !== w.id).slice(0, 8).map(id => byId.get(id)).filter(Boolean);",
    "    const rel = relIds(ch, new Set([w.id])).slice(0, 8).map(id => byId.get(id)).filter(Boolean);")
# 6) 홈: 맨 위(약점 아래)에 0부 · 기본, 다음 순서 추천도 기본 장부터
rep("installHint() + weakTopHTML() + banner + partsHTML() +", "installHint() + weakTopHTML() + banner + basicHTML() + partsHTML() +")
rep("  for (const c of CHAPTERS) { if (c.kind === 'all') continue; (parts[c.part] = parts[c.part] || []).push(c); }",
    "  for (const c of CHAPTERS) { if (c.kind === 'all' || c.basic) continue; (parts[c.part] = parts[c.part] || []).push(c); }")
rep("  const all = CHAPTERS.find(c => c.kind === 'all');", "  const all = CHAPTERS.find(c => c.kind === 'all' && !c.basic);")
rep("function partsHTML() {",
    "function basicHTML() {\n"
    "  if (!BTOTAL) return '';\n"
    "  const cs = CHAPTERS.filter(c => c.basic), parts = [];\n"
    "  cs.forEach(c => { if (c.kind !== 'all') (parts[c.part] = parts[c.part] || []).push(c); });\n"
    "  const allc = cs.find(c => c.kind === 'all');\n"
    "  return parts.map((ps, p) => {\n"
    "    const a = p * 500 + 1, b = Math.min(BTOTAL, a + 499);\n"
    "    return '<section class=\"grp grp-basic\"><div class=\"grp-h\"><b>0부 · 기본' + (parts.length > 1 ? ' ' + (p + 1) : '') + '</b><span>기본 ' + a + '–' + b + '</span><i class=\"rule\"></i></div>' +\n"
    "      (p === 0 ? '<p class=\"part-h\">N5·N4 단어 중 BJT에 나오는 기초 단어 · 1500 단어와 겹치는 건 같은 카드 · 250개씩 50개 단위로 쌓아 가며 회독</p>' : '') +\n"
    "      '<div class=\"books\">' + ps.map(c => bookHTML(c)).join('') + '</div></section>';\n"
    "  }).join('') + (allc ? '<section class=\"grp grp-basic\"><div class=\"grp-h\"><b>기본 전체 총정리</b><span>기본 1–' + BTOTAL + '</span><i class=\"rule\"></i></div><div class=\"books\">' + bookHTML(allc) + '</div></section>' : '');\n"
    "}\n"
    "function partsHTML() {")
rep("const suggestNext = () => { for (const c of CHAPTERS) {", "const suggestNext = () => { for (const c of CHAPTERS.filter(c => c.basic).concat(CHAPTERS.filter(c => !c.basic))) {")
rep("  for (const id of ORDER) { const x = H.w[id]; if (x && x.l !== -1) { seen++; if (x.l === 1) okN++; } }",
    "  for (const id of ALL_IDS) { const x = H.w[id]; if (x && x.l !== -1) { seen++; if (x.l === 1) okN++; } }")
rep("<span>단어 회독 ' + TOTAL.toLocaleString() + '</span></div>'", "<span>단어 회독 ' + TOTAL.toLocaleString() + (BTOTAL ? '<small class=\"b-sub2\"> + 기본 ' + BTOTAL + '</small>' : '') + '</span></div>'")
rep("<span>전체 단어 목록</span><small>' + TOTAL.toLocaleString() + '</small>", "<span>전체 단어 목록</span><small>' + ALLN.toLocaleString() + '</small>")
rep("<span>본 단어 <b>' + seen + '</b>/' + TOTAL + '</span>", "<span>본 단어 <b>' + seen + '</b>/' + ALLN + '</span>")
rep("        '<li><b>번호가 앞일수록 BJT 핵심</b>이에요. 시간이 모자라면 앞에서부터.</li>' +\n",
    "        '<li><b>번호가 앞일수록 BJT 핵심</b>이에요. 시간이 모자라면 앞에서부터.</li>' +\n"
    "        (BTOTAL ? '<li><b>0부 · 기본</b>: N5·N4 단어 중 BJT 지문·청해에 나오는 기초 단어(' + BTOTAL + '개). 1500 단어와 겹치는 단어는 같은 카드라 기록이 같이 쌓여요. 예문 아래 ‘단어’ 풀이와 같이 보세요.</li>' : '') +\n")
rep("' · 단어 ' + TOTAL.toLocaleString() + '개</p>'", "' · 단어 ' + TOTAL.toLocaleString() + '개' + (BTOTAL ? ' + 기본 ' + BTOTAL + '개' : '') + '</p>'")
# 7) 시험일 10/22(목)로: 기본값 + 예전 기본값(10/13)이면 한 번만 옮김
rep("const DEF_EXAM = '2026-10-13';", "const DEF_EXAM = '2026-10-22';")
rep("  if (o.em === 1 || o.em === 2) r.em = o.em;", "  if (o.em === 1 || o.em === 2 || o.em === 3) r.em = o.em;")
rep("if (!(S.em >= 2)) { if (S.exam === '2026-10-07' || S.exam === '2026-10-08') S.exam = '2026-10-13'; S.em = 2; LS.set(KS, S); }",
    "if (!(S.em >= 2)) { if (S.exam === '2026-10-07' || S.exam === '2026-10-08') S.exam = '2026-10-13'; S.em = 2; LS.set(KS, S); }\n"
    "if (!(S.em >= 3)) { if (S.exam === '2026-10-13') S.exam = '2026-10-22'; S.em = 3; LS.set(KS, S); }")
CSS_1013 = """
.t-K{border-style:dashed;font-size:11px;letter-spacing:-.02em}
.brand .b-sub2{font-size:.82em;color:var(--ink-3);font-weight:500}
"""
rep('</style>\n</head>', CSS_1013 + '</style>\n</head>')
rep("window.__t = {get ui() { return ui; },", "window.__t = {get ui() { return ui; }, CHAPTERS,")
# ================= 10/13: 다시 녹음한 음성이 아이패드에 저장된 옛 음성에 막히지 않게 =================
# 음성은 서비스워커가 '저장본 먼저'로 영구 보관 → 같은 주소로 파일만 바꾸면 기기는 옛 음성을 계속 틂.
# 그래서 다시 녹음하는 파일(기본 카드 음성)은 주소 뒤에 파일 내용 해시(?v=)를 붙이고, 옛 저장본은 지움.
rep("const AUDIO_MB = '__AUDIO_MB__';",
    "const AUDIO_MB = '__AUDIO_MB__';\n"
    "/* 다시 녹음한 음성: 파일 내용 해시를 주소에 붙여(?v=) 기기에 저장된 옛 음성 대신 새 음성을 받게 함 */\n"
    "const AV = DATA.av || {}, AVH = DATA.avh || '';")
rep("  url(kind, id, i) { return new URL('audio/' + (kind === 'w' ? 'w/' + id : 's/' + id + '-' + i) + '.mp3', location.href).href; },",
    "  url(kind, id, i) { const k = kind === 'w' ? 'w/' + id : 's/' + id + '-' + i; return new URL('audio/' + k + '.mp3' + (AV[k] ? '?v=' + AV[k] : ''), location.href).href; },")
rep("const sayWord = id => {",
    "/* 옛 저장본 정리: 해시가 달라진(또는 해시 없이 저장된) 기본 카드 음성을 지움. 음성 버전(AVH)이 바뀔 때 한 번만 */\n"
    "function audioPrune() {\n"
    "  if (!AUD.on || !AVH || !('caches' in window)) return Promise.resolve(0);\n"
    "  let seen = ''; try { seen = localStorage.getItem('bjt500.avh') || ''; } catch (e) {}\n"
    "  if (seen === AVH) return Promise.resolve(0);\n"
    "  let n = 0;\n"
    "  return caches.open(AUDIO_CACHE).then(c => c.keys().then(reqs => Promise.all(reqs.map(r => {\n"
    "    let u; try { u = new URL(r.url); } catch (e) { return null; }\n"
    "    const m = /\\/audio\\/(w\\/\\d+|s\\/\\d+-\\d+)\\.mp3$/.exec(u.pathname);\n"
    "    if (!m) return null;\n"
    "    const want = AV[m[1]] ? '?v=' + AV[m[1]] : '';\n"
    "    if (u.search === want) return null;\n"
    "    n++; return c.delete(r);\n"
    "  })))).then(() => { try { localStorage.setItem('bjt500.avh', AVH); } catch (e) {} return n; }).catch(() => 0);\n"
    "}\n"
    "setTimeout(audioPrune, 5000);\n"
    "const sayWord = id => {")
rep("  const done = saved.indexOf(AUDIO_CACHE + '|' + AUDIO_TOTAL + '|') === 0;",
    "  const done = saved.indexOf(AUDIO_CACHE + '|' + AUDIO_TOTAL + '|' + AVH + '|') === 0;")
rep("localStorage.setItem('bjt500.audio', AUDIO_CACHE + '|' + AUDIO_TOTAL + '|' + Date.now());",
    "localStorage.setItem('bjt500.audio', AUDIO_CACHE + '|' + AUDIO_TOTAL + '|' + AVH + '|' + Date.now());")
rep("window.__t = {get ui() { return ui; }, CHAPTERS,", "window.__t = {get ui() { return ui; }, CHAPTERS, AUD, AV, AVH, audioPrune,")
exec(open('/home/claude/work/app/patch_1015.py', encoding='utf-8').read())
exec(open('/home/claude/work/app/patch_1015b.py', encoding='utf-8').read())
exec(open('/home/claude/work/app/patch_1016.py', encoding='utf-8').read())
exec(open('/home/claude/work/app/patch_1017.py', encoding='utf-8').read())
exec(open('/home/claude/work/app/patch_1018.py', encoding='utf-8').read())
exec(open('/home/claude/work/app/patch_1021.py', encoding='utf-8').read())
exec(open('/home/claude/work/app/patch_1113.py', encoding='utf-8').read())
exec(open('/home/claude/work/app/patch_1113b.py', encoding='utf-8').read())
exec(open('/home/claude/work/app/patch_1113c.py', encoding='utf-8').read())
exec(open('/home/claude/work/app/patch_1114.py', encoding='utf-8').read())
open(DST, 'w', encoding='utf-8').write(s)
print('ok, replacements:', n_rep, 'size', len(s))
