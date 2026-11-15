# 11/15 한자 연결 점검(사용자 11/13·11/15: '같은 한자가 제대로 안 된 경우 · 한자 카드에 있어야 할 단어가 없는 경우 등' → 전체에서 직접 찾아 고치기)
# 1) 같은 한자 순서: N3·N2 단어(본편·기본 번호 없음)는 정렬 값이 NaN이라 순서가 뒤죽박죽이었음 → 번호로 정렬.
#    BJT 칸(본편 장 · 1~3부 약점 · BJT에만 있는 단어)은 예전 순서 그대로(닻 기본 2개 → 본편 1,500 → 나머지).
#    그 밖(기본·N3·N2 단어)은 BJT식 대신 닻 기본 2개 → 기본 → N3 → N2(본 것 먼저, 번호 순) → BJT에만 있는 단어.
# 2) 한자 카드 맨 아래 '이 한자가 든 단어': 본편 → 기본 → N3·N2 순이던 것을 공부 순서(기본 → N3 → N2 → BJT에만 있는 단어)로.

rep("const SK_N = 6;\nfunction relIds(c, skip) {\n"
    "  const ids = K[c].u.filter(id => byId.has(id) && !skip.has(id));\n"
    "  const seen = id => { const x = H.w[id]; return x && x.l !== -1 ? 1 : 0; };\n"
    "  const anchor = ids.filter(id => BNO.has(id)).sort((a, b) => BNO.get(a) - BNO.get(b)).slice(0, 2), an = new Set(anchor);\n"
    "  const main = ids.filter(id => NO.has(id) && !an.has(id)).sort((a, b) => (seen(b) - seen(a)) || (NO.get(a) - NO.get(b)));\n"
    "  const rest = ids.filter(id => !NO.has(id) && !an.has(id)).sort((a, b) => (seen(b) - seen(a)) || (BNO.get(a) - BNO.get(b)));\n"
    "  return anchor.concat(main, rest);\n}",
    "const SK_N = 6;\n"
    "/* 11/15 같은 한자 순서 — BJT 칸(본편 장·1~3부 약점·BJT에만 있는 단어)은 예전 그대로: 닻(기본 2개) → 본편 1,500 → 나머지(기본 → N3 → N2).\n"
    "   그 밖(기본·N3·N2)은 닻(기본 2개) → 기본 → N3 → N2 → BJT에만 있는 단어. 묶음 안에서는 본 것 먼저, 번호 순. */\n"
    "function relBjt(w, inSheet) {\n"
    "  if (!w) return true;\n"
    "  if (!inSheet && ctx && view === 'study' && ui.id === w.id) {\n"
    "    if (ctx.kind === 'ch') { const ch = CHAPTERS[ctx.i]; return !!ch && !ch.basic && !ch.lv; }\n"
    "    if (ctx.kind === 'weak' && ctx.g) return /^p\\d+$/.test(ctx.g);\n"
    "  }\n"
    "  return NO.has(w.id) && !BNO.has(w.id) && !LNO.has(w.id);\n"
    "}\n"
    "function relIds(c, skip, w, inSheet) {\n"
    "  const ids = K[c].u.filter(id => byId.has(id) && !skip.has(id));\n"
    "  const seen = id => { const x = H.w[id]; return x && x.l !== -1 ? 1 : 0; };\n"
    "  const anchor = ids.filter(id => BNO.has(id)).sort((a, b) => BNO.get(a) - BNO.get(b)).slice(0, 2), an = new Set(anchor);\n"
    "  if (relBjt(w, inSheet)) {\n"
    "    const main = ids.filter(id => NO.has(id) && !an.has(id)).sort((a, b) => (seen(b) - seen(a)) || (NO.get(a) - NO.get(b)));\n"
    "    const rest = ids.filter(id => !NO.has(id) && !an.has(id)).sort((a, b) => (seen(b) - seen(a)) || (jptNo(a) - jptNo(b)));\n"
    "    return anchor.concat(main, rest);\n"
    "  }\n"
    "  const jpt = ids.filter(id => !an.has(id) && (BNO.has(id) || LNO.has(id))).sort((a, b) => (seen(b) - seen(a)) || (jptNo(a) - jptNo(b)));\n"
    "  const bj = ids.filter(id => !an.has(id) && !BNO.has(id) && !LNO.has(id)).sort((a, b) => (seen(b) - seen(a)) || (jptNo(a) - jptNo(b)));\n"
    "  return anchor.concat(jpt, bj);\n}")
rep("function skHTML(w) {", "function skHTML(w, inSheet) {")
rep("    const ids = relIds(c, shown);", "    const ids = relIds(c, shown, w, inSheet);")
rep("    const rel = relIds(ch, new Set([w.id])).slice(0, 8)", "    const rel = relIds(ch, new Set([w.id]), w).slice(0, 8)")
rep("storyHTML(w, 's-story') + skHTML(w) + ptHTML(w)", "storyHTML(w, 's-story') + skHTML(w, inSheet) + ptHTML(w)")
# 공부 순서 번호: 기본 → N3 → N2 → BJT에만 있는 단어(겹치는 카드는 앞 칸 번호)
rep("const sortNo = id => ",
    "const jptNo = id => BNO.has(id) ? BNO.get(id) : LNO.has(id) ? 2000 + (LNO.get(id).L === 3 ? 0 : 2000) + LNO.get(id).n : 9000 + (NO.has(id) ? NO.get(id) : 0);\n"
    "const sortNo = id => ")
rep("/* ----- 한자 카드(시트·해설 공통): 카드 + 맨 아래 이 한자가 든 단어 전부(본편 순서 → 기본 순서) ----- */",
    "/* ----- 한자 카드(시트·해설 공통): 카드 + 맨 아래 이 한자가 든 단어 전부(11/15: 공부 순서 기본 → N3 → N2 → BJT에만 있는 단어) ----- */")
rep("  const ids = [...new Set(Array.isArray(k.u) ? k.u : [])].filter(id => byId.has(id)).sort((a, b) => sortNo(a) - sortNo(b));\n  if (!ids.length) return '';\n  return '<section class=\"kzu-ws\">",
    "  const ids = [...new Set(Array.isArray(k.u) ? k.u : [])].filter(id => byId.has(id)).sort((a, b) => jptNo(a) - jptNo(b));\n  if (!ids.length) return '';\n  return '<section class=\"kzu-ws\">")
