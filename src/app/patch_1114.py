# 11/14 (11/13 밤 페이지) — 사용자: JPT로 방향 전환. 기본(N5·N4) → BJT → N3 → N2 → 한자, 등급 표시 겹치기, 약점을 500개 묶음별로
# 1) N3·N2 칸: 단어의 jl(3·2) + jn(칸 안 번호, 1부터 빈틈없이). 기본(bn) 카드는 안 들어감. BJT와 겹치는 카드는 같은 카드(기록 같이)
#    장 키 'N3:'+단어 지문+범위+종류 → 기존 장(본편 PSIG·기본 'B:') 키는 그대로
# 2) 카드 표시: 기본 · BJT S/A/B · N3/N2 를 해당하는 만큼 겹쳐서(tierTag → tagsHTML)
# 3) 500개 묶음(접기 하나)마다 약점: 묶음 안 약점 수(접기 머리 ★n) + 복습·이어서·목록. 묶음별 복습 진행은 H.wrp[묶음 키](동기화 H.wrpu)
#    맨 위 전체 약점 상자는 그대로(H.wr)
# 4) 다음 순서 추천: 기본 → N3 → N2 → BJT

# ---------- CSS ----------
rep('@media (prefers-reduced-motion:no-preference){',
    '.tb-t+.tb-t{margin-left:4px}\n'
    '.t-L{border-color:var(--stamp);color:var(--stamp)}\n'
    '.gf .g-wk{font-size:13px;font-weight:700;color:var(--ink-2)}\n'
    '.pw{display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin:2px 0 12px;padding:10px 12px;border:1px dashed var(--line);border-radius:12px}\n'
    '.pw b{font-size:15px}\n.pw .pw-n{font-size:13px;color:var(--ink-3)}\n.pw .grow{flex:1}\n'
    '@media (prefers-reduced-motion:no-preference){')

# ---------- 데이터: N3·N2 순서 ----------
rep("const BTOTAL = BORDER.length;\nconst ALL_IDS = ORDER.concat(BORDER.filter(id => !NO.has(id)));\n",
    "const BTOTAL = BORDER.length;\n"
    "/* 11/14 N3·N2 칸: jl(3·2) + jn(칸 안 번호). 기본(bn) 카드는 안 들어감. BJT·기본과 겹치는 카드는 같은 카드라 기록이 같이 쌓임 */\n"
    "const LV = [3, 2];\n"
    "const LORDER = {};\n"
    "LV.forEach(L => { LORDER[L] = W.filter(w => w.jl === L && w.jn != null).sort((a, b) => a.jn - b.jn).map(w => w.id); });\n"
    "const LNO = new Map();\n"
    "LV.forEach(L => LORDER[L].forEach((id, i) => { if (!LNO.has(id)) LNO.set(id, {L, n: i + 1}); }));\n"
    "const LTOTAL = LV.reduce((n, L) => n + LORDER[L].length, 0);\n"
    "const ALL_IDS = ORDER.concat(BORDER.filter(id => !NO.has(id)), [].concat(...LV.map(L => LORDER[L])).filter(id => !NO.has(id) && !BNO.has(id)));\n")
rep("const numLabel = id => NO.has(id) ? 'No.' + NO.get(id) + (BNO.has(id) ? ' · 기본 ' + BNO.get(id) : '') : '기본 ' + BNO.get(id);\n"
    "const rowNum = id => NO.has(id) ? NO.get(id) : '기' + BNO.get(id);\n"
    "const sortNo = id => NO.has(id) ? NO.get(id) : TOTAL + (BNO.get(id) || 0);\n",
    "const lvLab = id => { const l = LNO.get(id); return l ? 'N' + l.L + ' ' + l.n : ''; };\n"
    "const numLabel = id => [NO.has(id) ? 'No.' + NO.get(id) : '', BNO.has(id) ? '기본 ' + BNO.get(id) : '', lvLab(id)].filter(Boolean).join(' · ');\n"
    "const rowNum = id => NO.has(id) ? NO.get(id) : BNO.has(id) ? '기' + BNO.get(id) : LNO.has(id) ? 'N' + LNO.get(id).L + '·' + LNO.get(id).n : '';\n"
    "const sortNo = id => NO.has(id) ? NO.get(id) : BNO.has(id) ? TOTAL + BNO.get(id) : TOTAL + 5000 + (LNO.has(id) ? (LNO.get(id).L === 3 ? 0 : 5000) + LNO.get(id).n : 0);\n")

# ---------- 장: N3·N2 ----------
rep("const BCH0 = CHAPTERS.length;\n", "const BCH0 = CHAPTERS.length, LCH0 = {};\n")
rep("basic: true, key: 'B:' + hs(ids) + ':' + c.a + '-' + c.b + ':' + c.kind})); });\n})();\n",
    "basic: true, key: 'B:' + hs(ids) + ':' + c.a + '-' + c.b + ':' + c.kind})); });\n"
    "  LV.forEach(L => { LCH0[L] = CHAPTERS.length; genChapters(LORDER[L].length).forEach(c => { const ids = LORDER[L].slice(c.a - 1, c.b); CHAPTERS.push(Object.assign(c, {i: CHAPTERS.length, ids, cnt: ids.length, lv: L, key: 'N' + L + ':' + hs(ids) + ':' + c.a + '-' + c.b + ':' + c.kind})); }); });\n"
    "})();\n")
rep("const chName = i => CHAPTERS[i] && CHAPTERS[i].basic ? '基本' + (i - BCH0 + 1) + '章' : '第' + (i + 1) + '章';\n"
    "const chRange = c => (c.basic ? '기본 ' : 'No.') + c.a + '–' + c.b;\n",
    "const chName = i => { const c = CHAPTERS[i]; return c && c.lv ? 'N' + c.lv + '·' + (i - LCH0[c.lv] + 1) + '章' : c && c.basic ? '基本' + (i - BCH0 + 1) + '章' : '第' + (i + 1) + '章'; };\n"
    "const chRange = c => (c.lv ? 'N' + c.lv + ' ' : c.basic ? '기본 ' : 'No.') + c.a + '–' + c.b;\n"
    "/* 11/14 500개 묶음(홈의 작은 접기 하나) → 이름·단어: 묶음별 약점 */\n"
    "const PARTS = new Map();\n"
    "for (let p = 0; p * 500 < TOTAL; p++) PARTS.set('p' + p, {name: (p + 1) + '부', ids: ORDER.slice(p * 500, p * 500 + 500)});\n"
    "for (let p = 0; p * 500 < BTOTAL; p++) PARTS.set('b' + p, {name: '기본 ' + (p + 1), ids: BORDER.slice(p * 500, p * 500 + 500)});\n"
    "LV.forEach(L => { for (let p = 0; p * 500 < LORDER[L].length; p++) PARTS.set('l' + L + '_' + p, {name: 'N' + L + ' ' + (p + 1) + '부', ids: LORDER[L].slice(p * 500, p * 500 + 500)}); });\n"
    "PARTS.forEach(v => { v.set = new Set(v.ids); });\n"
    "const pName = g => PARTS.has(g) ? PARTS.get(g).name : '';\n")

# ---------- 진도: 묶음별 약점 복습 ----------
rep("const blankH = () => ({ch: {}, w: {}, wr: null, wru: 0, ", "const blankH = () => ({ch: {}, w: {}, wr: null, wru: 0, wrp: {}, wrpu: {}, ")
rep("  h.wr = cleanRun(o.wr); h.wru = nn(o.wru);\n",
    "  h.wr = cleanRun(o.wr); h.wru = nn(o.wru);\n"
    "  { const wp = obj(o.wrp), wpu = obj(o.wrpu); for (const k in wp) if (PARTS.has(k)) { const r = cleanRun(wp[k]); if (r) h.wrp[k] = r; } for (const k in wpu) if (PARTS.has(k)) h.wrpu[k] = nn(wpu[k]); }\n")
rep("  if (rwru > H.wru) { H.wr = cleanRun(R.wr); H.wru = rwru; res.changed = true; } else if (H.wru > rwru) res.localNewer = true;\n",
    "  if (rwru > H.wru) { H.wr = cleanRun(R.wr); H.wru = rwru; res.changed = true; } else if (H.wru > rwru) res.localNewer = true;\n"
    "  { const rpu = obj(R.wrpu), rp = obj(R.wrp);\n"
    "    for (const k in rpu) { if (!PARTS.has(k)) continue; const t = nn(rpu[k]), l = H.wrpu[k] || 0; if (t > l) { const r = cleanRun(rp[k]); if (r) H.wrp[k] = r; else delete H.wrp[k]; H.wrpu[k] = t; res.changed = true; } else if (l > t) res.localNewer = true; }\n"
    "    for (const k in H.wrpu) if (!(k in rpu)) res.localNewer = true; }\n")
rep("const ctxKey = () => ctx ? (ctx.kind === 'ch' ? 'ch' + ctx.i : 'weak') : '';\n"
    "function getRun() { if (!ctx) return null; return ctx.kind === 'ch' ? (H.ch[ctx.i] ? H.ch[ctx.i].cur : null) : H.wr; }\n"
    "function setRun(r) { if (ctx.kind === 'ch') chGet(ctx.i).cur = r; else H.wr = r; }\n",
    "const ctxKey = () => ctx ? (ctx.kind === 'ch' ? 'ch' + ctx.i : 'weak' + (ctx.g ? ':' + ctx.g : '')) : '';\n"
    "function getRun() { if (!ctx) return null; return ctx.kind === 'ch' ? (H.ch[ctx.i] ? H.ch[ctx.i].cur : null) : ctx.g ? (H.wrp[ctx.g] || null) : H.wr; }\n"
    "function setRun(r) { if (ctx.kind === 'ch') chGet(ctx.i).cur = r; else if (ctx.g) { if (r) H.wrp[ctx.g] = r; else delete H.wrp[ctx.g]; } else H.wr = r; }\n")
rep("function touch(r, now) { r.u = now; if (ctx.kind === 'ch') chGet(ctx.i).u = now; else H.wru = now; }\n",
    "function touch(r, now) { r.u = now; if (ctx.kind === 'ch') chGet(ctx.i).u = now; else if (ctx.g) H.wrpu[ctx.g] = now; else H.wru = now; }\n")
rep("function openWeak(fresh) {\n"
    "  const ids = weakIds(), now = Date.now();\n"
    "  if (fresh || !H.wr) {\n"
    "    if (!ids.length) { toast('약점 단어가 아직 없어요'); return; }\n"
    "    H.wr = newRun(weakOrder(ids), false); H.wru = now; saveH();\n"
    "  }\n"
    "  ctx = {kind: 'weak'}; undoStack = [];\n",
    "const partWeak = g => { const P = PARTS.get(g); return P ? weakIds().filter(id => P.set.has(id)) : weakIds(); };\n"
    "function openWeak(fresh, g) {\n"
    "  g = g && PARTS.has(g) ? g : '';\n"
    "  const ids = partWeak(g), now = Date.now(), cur = g ? H.wrp[g] : H.wr;\n"
    "  if (fresh || !cur) {\n"
    "    if (!ids.length) { toast(g ? pName(g) + '에 약점 단어가 없어요' : '약점 단어가 아직 없어요'); return; }\n"
    "    const r = newRun(weakOrder(ids), false);\n"
    "    if (g) { H.wrp[g] = r; H.wrpu[g] = now; } else { H.wr = r; H.wru = now; }\n"
    "    saveH();\n"
    "  }\n"
    "  ctx = {kind: 'weak', g}; undoStack = [];\n")
rep("  } else { H.wr = null; H.wru = now; info = {kind: 'weak'}; }\n",
    "  } else { if (ctx.g) { delete H.wrp[ctx.g]; H.wrpu[ctx.g] = now; } else { H.wr = null; H.wru = now; } info = {kind: 'weak', g: ctx.g || ''}; }\n")
rep("  if (H.wr && (!best || H.wr.u > best.u)) best = {kind: 'weak', u: H.wr.u, r: H.wr};\n",
    "  if (H.wr && (!best || H.wr.u > best.u)) best = {kind: 'weak', u: H.wr.u, r: H.wr};\n"
    "  for (const k in H.wrp) { const r = H.wrp[k]; if (r && (!best || r.u > best.u)) best = {kind: 'weak', g: k, u: r.u, r}; }\n")
rep("case 'resume': { const r = findResume(); if (!r) break; if (r.kind === 'ch') openChapter(r.i, false); else openWeak(false); break; }",
    "case 'resume': { const r = findResume(); if (!r) break; if (r.kind === 'ch') openChapter(r.i, false); else openWeak(false, r.g); break; }")
rep("    const name = res.kind === 'ch' ? chName(res.i) + ' · ' + (chGet(res.i).n + 1) + '회독' : '약점 복습';\n",
    "    const name = res.kind === 'ch' ? chName(res.i) + ' · ' + (chGet(res.i).n + 1) + '회독' : '약점 복습' + (res.g ? ' · ' + pName(res.g) : '');\n")
rep("  const title = ctx.kind === 'ch' ? chName(ctx.i) + ' · ' + (chGet(ctx.i).n + 1) + '회독' : '약점 복습';\n",
    "  const title = ctx.kind === 'ch' ? chName(ctx.i) + ' · ' + (chGet(ctx.i).n + 1) + '회독' : '약점 복습' + (ctx.g ? ' · ' + pName(ctx.g) : '');\n")
rep("'약점 복습 완료'", "'약점 복습' + (info.g ? ' · ' + pName(info.g) : '') + ' 완료'")
rep("    rows = '<dt>복습</dt><dd>약점 단어</dd>';\n",
    "    rows = '<dt>복습</dt><dd>약점 단어' + (info.g ? ' · ' + pName(info.g) : '') + '</dd>';\n")
rep("    acts = '<button class=\"btn primary\" data-act=\"weakView\">약점 목록 보기</button>",
    "    acts = '<button class=\"btn primary\" data-act=\"weakView\" data-pg=\"' + (info.g || '') + '\">약점 목록 보기</button>")
# 약점 목록: B.wg(묶음 키, ''=전체)
rep("const B = {q: '', tier: 'all', st: 'all', cat: 'all', mask: false, wmask: false, smask: false, wsel: false, wpick: new Set()};",
    "const B = {q: '', tier: 'all', st: 'all', cat: 'all', mask: false, wmask: false, smask: false, wsel: false, wpick: new Set(), wg: ''};")
rep("  const n = B.wpick.size, ids = weakIds();\n", "  const n = B.wpick.size, ids = partWeak(B.wg || '');\n")
rep("  const prevWr = all && H.wr ? JSON.stringify(H.wr) : null;\n",
    "  const g = view === 'weak' ? (B.wg || '') : '';\n"
    "  const prevWr = all && (g ? H.wrp[g] : H.wr) ? JSON.stringify(g ? H.wrp[g] : H.wr) : null;\n")
rep("  if (all) { H.wr = null; H.wru = now; }\n",
    "  if (all) { if (g) { delete H.wrp[g]; H.wrpu[g] = now; } else { H.wr = null; H.wru = now; } }\n")
rep("    if (prevWr) { H.wr = cleanRun(JSON.parse(prevWr)); H.wru = t; }\n",
    "    if (prevWr) { const pr = cleanRun(JSON.parse(prevWr)); if (g) { if (pr) H.wrp[g] = pr; H.wrpu[g] = t; } else { H.wr = pr; H.wru = t; } }\n")
rep("function renderWeak() {\n  const ids = weakIds(), wr = H.wr;\n",
    "function renderWeak() {\n"
    "  if (B.wg && !PARTS.has(B.wg)) B.wg = '';\n"
    "  const g = B.wg || '', ids = partWeak(g), wr = g ? H.wrp[g] : H.wr, pg = ' data-pg=\"' + g + '\"';\n")
rep("'<button class=\"btn primary big\" data-act=\"weakGo\">이어서 · ' + progText(wr) + '</button><button class=\"btn big\" data-act=\"weakNew\"' + (ids.length ? '' : ' disabled') + '>처음부터 (",
    "'<button class=\"btn primary big\" data-act=\"weakGo\"' + pg + '>이어서 · ' + progText(wr) + '</button><button class=\"btn big\" data-act=\"weakNew\"' + pg + (ids.length ? '' : ' disabled') + '>처음부터 (")
rep(": '<button class=\"btn primary big\" data-act=\"weakNew\"' + (ids.length ? '' : ' disabled') + '>카드로 복습 · ' + ids.length + '개 (많이 틀린 순)</button>') +",
    ": '<button class=\"btn primary big\" data-act=\"weakNew\"' + pg + (ids.length ? '' : ' disabled') + '>카드로 복습 · ' + ids.length + '개 (많이 틀린 순)</button>') +\n"
    "        (g ? '<button class=\"btn big\" data-act=\"weakView\" data-pg=\"\">전체 약점 보기</button>' : '') +")
rep("<h1 class=\"bar-title\">약점 단어 ' + ids.length + '</h1>",
    "<h1 class=\"bar-title\">약점 단어' + (g ? ' · ' + pName(g) : '') + ' ' + ids.length + '</h1>")
rep("case 'weakView': closeModal(); closeSheet(); show('weak'); break;",
    "case 'weakView': B.wg = el.dataset.pg || ''; B.wsel = false; B.wpick = new Set(); closeModal(); closeSheet(); show('weak'); break;")
rep("case 'weakGo': openWeak(false); break;", "case 'weakGo': openWeak(false, el.dataset.pg || ''); break;")
rep("case 'weakNew': openWeak(true); break;", "case 'weakNew': openWeak(true, el.dataset.pg || ''); break;")
rep("case 'wselAll': { const ids = weakIds();", "case 'wselAll': { const ids = partWeak(B.wg || '');")
rep("case 'wdelAll': { const ids = weakIds();", "case 'wdelAll': { const ids = partWeak(B.wg || '');")

# ---------- 홈: 묶음별 약점 줄 + N3·N2 칸 ----------
rep("function foldHTML(key, cls, title, range, cs, inner, st) {",
    "function foldHTML(key, cls, title, range, cs, inner, st, wk) {")
rep("<span class=\"g-p\">끝낸 장 ' + done + '/' + cs.length + '</span>' + (on ? '<span class=\"g-on\">진행중</span>' : '') +",
    "<span class=\"g-p\">끝낸 장 ' + done + '/' + cs.length + '</span>' + (wk ? '<span class=\"g-wk\">★ ' + wk + '</span>' : '') + (on ? '<span class=\"g-on\">진행중</span>' : '') +")
rep("parts.map((ps, p) => { const s = sub(p); return foldHTML(s.key, cls, s.title, s.range, ps, '<div class=\"books\">' + ps.map(c => bookHTML(c)).join('') + '</div>'); }).join('') +",
    "parts.map((ps, p) => { const s = sub(p), wk = PARTS.has(s.key) ? partWeak(s.key).length : 0; return foldHTML(s.key, cls, s.title, s.range, ps, pwHTML(s.key, wk) + '<div class=\"books\">' + ps.map(c => bookHTML(c)).join('') + '</div>', null, wk); }).join('') +")
rep("function basicHTML() {",
    "/* 11/14 묶음 안 약점 줄: 이 묶음 약점 n개 · 이어서/복습 · 목록 */\n"
    "function pwHTML(key, n) {\n"
    "  if (!PARTS.has(key)) return '';\n"
    "  const r = H.wrp[key], pg = ' data-pg=\"' + key + '\"';\n"
    "  return '<div class=\"pw\"><b>★ 이 묶음 약점 ' + n + '개</b>' + (n ? '' : '<span class=\"pw-n\">' + S.wkN + '번 이상 모르면 여기 모여요</span>') + '<span class=\"grow\"></span>' +\n"
    "    (r ? '<button class=\"btn primary\" data-act=\"weakGo\"' + pg + '>이어서 · ' + progText(r) + '</button>' : '') +\n"
    "    '<button class=\"btn' + (r ? '' : ' primary') + '\" data-act=\"weakNew\"' + pg + (n ? '' : ' disabled') + '>' + (r ? '처음부터' : '약점 복습') + '</button>' +\n"
    "    '<button class=\"btn\" data-act=\"weakView\"' + pg + (n ? '' : ' disabled') + '>목록</button></div>';\n"
    "}\n"
    "function lvHTML(L) {\n"
    "  const cs = CHAPTERS.filter(c => c.lv === L), T = LORDER[L].length;\n"
    "  if (!cs.length) return '';\n"
    "  return bigFoldHTML('L' + L, 'grp-lv', 'N' + L + ' 단어', 'N' + L + ' 1–' + T, 'JLPT N' + L + ' 단어(기본 제외) · 중요한 것부터 — 앞 1,000개가 핵심 · BJT·기본과 겹치는 건 같은 카드 · 250개씩 50개 단위로 쌓아 가며 회독', cs,\n"
    "    p => ({key: 'l' + L + '_' + p, title: 'N' + L + ' ' + (p + 1) + '부', range: 'N' + L + ' ' + (p * 500 + 1) + '–' + Math.min(T, p * 500 + 500)}), 'N' + L + ' 전체 총정리');\n"
    "}\n"
    "function basicHTML() {")
rep("  const cs = CHAPTERS.filter(c => !c.basic);\n  if (!cs.length) return '';\n  const lab =",
    "  const cs = CHAPTERS.filter(c => !c.basic && !c.lv);\n  if (!cs.length) return '';\n  const lab =")
rep("basicHTML() + partsHTML() + kzHomeHTML()", "basicHTML() + partsHTML() + lvHTML(3) + lvHTML(2) + kzHomeHTML()")
rep("const suggestNext = () => { for (const c of CHAPTERS.filter(c => c.basic).concat(CHAPTERS.filter(c => !c.basic))) {",
    "const suggestNext = () => { for (const c of CHAPTERS.filter(c => c.basic).concat(CHAPTERS.filter(c => c.lv === 3), CHAPTERS.filter(c => c.lv === 2), CHAPTERS.filter(c => !c.basic && !c.lv))) {")
rep("const nx0 = CHAPTERS[info.i + 1], nx = nx0 && !!nx0.basic === !!c.basic ? nx0 : null;",
    "const nx0 = CHAPTERS[info.i + 1], nx = nx0 && !!nx0.basic === !!c.basic && (nx0.lv || 0) === (c.lv || 0) ? nx0 : null;")
rep("guide = (c.basic ? '기본 ' + BTOTAL : TOTAL) + '개 전체 회독 완료.",
    "guide = (c.lv ? 'N' + c.lv + ' ' + LORDER[c.lv].length : c.basic ? '기본 ' + BTOTAL : TOTAL) + '개 전체 회독 완료.")
rep("(BTOTAL ? '<small class=\"b-sub2\"> + 기본 ' + BTOTAL + '</small>' : '')",
    "(BTOTAL ? '<small class=\"b-sub2\"> + 기본 ' + BTOTAL + (LTOTAL ? ' + N3·N2 ' + LTOTAL : '') + '</small>' : '')")
rep("(BTOTAL ? ' + 기본 ' + BTOTAL + '개' : '')", "(BTOTAL ? ' + 기본 ' + BTOTAL + '개' : '') + (LTOTAL ? ' + N3·N2 ' + LTOTAL + '개' : '')")
rep("(BTOTAL ? '<li><b>0부 · 기본</b>",
    "(LTOTAL ? '<li><b>N3 · N2</b>: JLPT N3·N2 단어(기본 제외)를 중요한 것부터 500개씩. 앞 1,000개가 핵심이에요. BJT·기본과 겹치는 단어는 같은 카드라 기록이 같이 쌓여요.</li>' : '') +\n        (BTOTAL ? '<li><b>0부 · 기본</b>")
rep("'<li>장을 넘나들며 합쳐서 ' + S.wkN + '번 이상 모르겠음 누른 단어는 맨 위 <b>약점 단어</b>에 자동으로 모여요(많이 틀린 순). ★로 직접 넣고 뺄 수도 있어요.</li>'",
    "'<li>장을 넘나들며 합쳐서 ' + S.wkN + '번 이상 모르겠음 누른 단어는 맨 위 <b>약점 단어</b>에 자동으로 모여요(많이 틀린 순). ★로 직접 넣고 뺄 수도 있어요. 500개 묶음을 펼치면 그 묶음 약점만 따로 복습할 수 있어요.</li>'")

# ---------- 카드 표시: 겹쳐 붙이기 ----------
rep("const tierTag = t =>", "const tagsHTML = id => { const w = byId.get(id), out = [];\n"
    "  if (BNO.has(id)) out.push('<b class=\"tb-t t-K\" title=\"기본 단어\">기본</b>');\n"
    "  if (NO.has(id)) out.push('<b class=\"tb-t' + (w.t === 'S' ? ' t-S' : '') + '\" title=\"BJT ' + w.t + '급\">BJT ' + w.t + '</b>');\n"
    "  const l = LNO.get(id); if (l) out.push('<b class=\"tb-t t-L\" title=\"JLPT N' + l.L + '\">N' + l.L + '</b>');\n"
    "  return out.join('') || tierTag(w && w.t); };\n"
    "const tierTag = t =>")
rep("tierTag(w.t)", "tagsHTML(w.id)", 4)

# ---------- 전체 단어 목록: N3·N2 거르기 ----------
rep("seg('tier', [['all', '전체'], ['S', 'S'], ['A', 'A'], ['B', 'B']].concat(BTOTAL ? [['K', '기본']] : []))",
    "seg('tier', [['all', '전체'], ['S', 'S'], ['A', 'A'], ['B', 'B']].concat(BTOTAL ? [['K', '기본']] : [], LORDER[3].length ? [['N3', 'N3']] : [], LORDER[2].length ? [['N2', 'N2']] : []))")
rep("if (B.tier !== 'all' && (B.tier === 'K' ? !BNO.has(id) : w.t !== B.tier)) continue;",
    "if (B.tier !== 'all' && (B.tier === 'K' ? !BNO.has(id) : B.tier === 'N3' || B.tier === 'N2' ? !(LNO.has(id) && 'N' + LNO.get(id).L === B.tier) : !(NO.has(id) && w.t === B.tier))) continue;")
