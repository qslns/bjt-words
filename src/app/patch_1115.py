# 11/14 K1 (11/14 새벽 페이지) — 사용자 11/13 22:35: 새 카드에서 새 한자가 생기니 한자 칸 배치를 다시(진도 새로 시작 OK)
# 한자 칸 순서 = kanji_mn/kzo_v2.json(expansion/lv/kanji_order.py): 그 한자가 처음 나오는 단어 칸(기본 → N3·N2 → BJT만), 같은 묶음 안은 신문 빈도 순
# DATA.kzg = [[묶음 이름, 수], …] → 장은 묶음마다 단어와 같은 규칙(250자 안 50자씩 + 묶음 총정리) + 맨 끝 한자 전체 총정리
# 그림 카드가 아직 없는 한자도 칸에 넣음(옛 꼴 카드 kzSimpleHTML) — 그림 카드는 나중에 채워도 순서·장 키가 안 바뀜
# 장 키는 그대로 'K:'+한자 지문+범위+종류 → 순서가 바뀐 장은 새 키(기록 새로 시작), 한자별 기록(KZ.w)은 글자 키라 그대로

rep("const KZN = KZO.length, KZNO = new Map(KZO.map((c, i) => [c, i + 1]));",
    "const KZN = KZO.length, KZNO = new Map(KZO.map((c, i) => [c, i + 1]));\n"
    "/* 11/14 K1 묶음: [이름, 수] — 수의 합이 KZN과 같을 때만 씀(아니면 예전처럼 한 줄) */\n"
    "const KZG = (() => { const g = Array.isArray(DATA.kzg) ? DATA.kzg.filter(x => Array.isArray(x) && typeof x[0] === 'string' && Number.isInteger(x[1]) && x[1] > 0) : []; return g.reduce((t, x) => t + x[1], 0) === KZN ? g : []; })();")
rep("const KZCH = genChapters(KZN).map((c, i) => { const ids = KZO.slice(c.a - 1, c.b); return Object.assign(c, {i, ids, cnt: ids.length, key: 'K:' + kzHs(ids) + ':' + c.a + '-' + c.b + ':' + c.kind}); });",
    "const KZCH = (() => {\n"
    "  let list;\n"
    "  if (KZG.length) {\n"
    "    list = []; let o = 0;\n"
    "    KZG.forEach((g, gi) => { for (const c of genChapters(g[1])) list.push({a: c.a + o, b: c.b + o, blk: c.blk, kind: c.kind === 'all' ? 'review' : c.kind, part: gi}); o += g[1]; });\n"
    "    if (KZN > 500) list.push({a: 1, b: KZN, blk: 'Z', kind: 'all', part: KZG.length});\n"
    "  } else list = genChapters(KZN);\n"
    "  return list.map((c, i) => { const ids = KZO.slice(c.a - 1, c.b); return Object.assign(c, {i, ids, cnt: ids.length, key: 'K:' + kzHs(ids) + ':' + c.a + '-' + c.b + ':' + c.kind}); });\n"
    "})();")
rep("    const inner = '<p class=\"part-h\">단어에 나오는 한자 ' + KZN + '자 · 많이 쓰는 순 · 250자 안에서 50자씩 쌓아 가며 회독 · 기록은 단어와 따로</p>' +\n"
    "      parts.map((ps, p) => (parts.length > 1 ? '<p class=\"kzu-ph\">' + (p * 500 + 1) + '–' + Math.min(KZN, p * 500 + 500) + '자</p>' : '') + '<div class=\"books\">' + ps.map(kzBookHTML).join('') + '</div>').join('') +",
    "    const goff = p => KZG.slice(0, p).reduce((t, g) => t + g[1], 0);\n"
    "    const inner = (KZG.length\n"
    "      ? '<p class=\"part-h\">단어에 나오는 한자 ' + KZN + '자 · 그 한자가 처음 나오는 단어 칸 순(' + KZG.map(g => g[0]).join(' → ') + '), 같은 묶음 안에서는 많이 쓰는 순 · 250자 안에서 50자씩 쌓아 가며 회독 · 기록은 단어와 따로</p>'\n"
    "      : '<p class=\"part-h\">단어에 나오는 한자 ' + KZN + '자 · 많이 쓰는 순 · 250자 안에서 50자씩 쌓아 가며 회독 · 기록은 단어와 따로</p>') +\n"
    "      parts.map((ps, p) => (KZG.length ? '<p class=\"kzu-ph\">' + esc(KZG[p][0]) + ' 한자 · ' + (goff(p) + 1) + '–' + (goff(p) + KZG[p][1]) + '자</p>' : parts.length > 1 ? '<p class=\"kzu-ph\">' + (p * 500 + 1) + '–' + Math.min(KZN, p * 500 + 500) + '자</p>' : '') + '<div class=\"books\">' + ps.map(kzBookHTML).join('') + '</div>').join('') +")
