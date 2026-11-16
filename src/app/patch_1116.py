# 11/16 N3 3부(1,001~1,500)·새 한자 178자 — 사용자는 N3·N2 앞 1,000만 볼 생각(11/13) → 칸이 1,000을 넘으면
# '앞 1,000 총정리'를 따로 남김(지금까지의 1–1,000 전체 총정리와 같은 장 키라 기록이 그대로 이어짐) + 새 전체 총정리.
# 한자도 같은 방식: 맨 뒤 'N3·N2 1,001~' 묶음을 뺀 1–1,434 총정리를 남기고(옛 전체 총정리 키 그대로) 1–1,612 전체 총정리를 더함.
rep("  LV.forEach(L => { LCH0[L] = CHAPTERS.length; genChapters(LORDER[L].length).forEach(c => {",
    "  LV.forEach(L => { LCH0[L] = CHAPTERS.length; const gl = genChapters(LORDER[L].length); if (LORDER[L].length > 1000) gl.splice(gl.length - 1, 0, {a: 1, b: 1000, blk: 'Z', kind: 'all', part: 0, core: true}); gl.forEach(c => {")
rep("  const all = cs.find(c => c.kind === 'all');\n  const inner = '<p class=\"part-h\">' + note + '</p>' +",
    "  const alls = cs.filter(c => c.kind === 'all');\n  const inner = '<p class=\"part-h\">' + note + '</p>' +")
rep("    (all ? '<p class=\"g-ph\">' + allName + '</p><div class=\"books\">' + bookHTML(all) + '</div>' : '');\n  return foldHTML(key, cls, title, range, cs, inner);",
    "    alls.map(c => '<p class=\"g-ph\">' + (c.core ? allName.replace('전체 총정리', '앞 1,000 총정리') : allName) + '</p><div class=\"books\">' + bookHTML(c) + '</div>').join('');\n  return foldHTML(key, cls, title, range, cs, inner);")
rep("    if (c.kind === 'all') guide = (c.lv ? 'N' + c.lv + ' ' + LORDER[c.lv].length : c.basic ? '기본 ' + BTOTAL : TOTAL) + '개 전체 회독 완료.",
    "    if (c.kind === 'all') guide = (c.lv ? 'N' + c.lv + ' ' + (c.core ? '앞 1,000' : LORDER[c.lv].length) : c.basic ? '기본 ' + BTOTAL : TOTAL) + '개 전체 회독 완료.")
rep("    if (KZN > 500) list.push({a: 1, b: KZN, blk: 'Z', kind: 'all', part: KZG.length});",
    "    const xg = KZG.length > 1 && /1,001/.test(KZG[KZG.length - 1][0]) ? KZG[KZG.length - 1][1] : 0;\n"
    "    if (xg && KZN - xg > 500) list.push({a: 1, b: KZN - xg, blk: 'Z', kind: 'all', part: KZG.length, core: true});\n"
    "    if (KZN > 500) list.push({a: 1, b: KZN, blk: 'Z', kind: 'all', part: KZG.length});")
rep("    const all = KZCH.find(c => c.kind === 'all');\n    const goff = p => KZG.slice(0, p).reduce((t, g) => t + g[1], 0);",
    "    const alls = KZCH.filter(c => c.kind === 'all');\n    const goff = p => KZG.slice(0, p).reduce((t, g) => t + g[1], 0);")
rep("      (all ? '<p class=\"kzu-ph\">한자 전체 총정리</p><div class=\"books\">' + kzBookHTML(all) + '</div>' : '');",
    "      alls.map(c => '<p class=\"kzu-ph\">' + (c.core ? '한자 1–' + c.b + '자 총정리(1,001번 이후 단어의 한자 빼고)' : '한자 전체 총정리') + '</p><div class=\"books\">' + kzBookHTML(c) + '</div>').join('');")
rep("  if (c.kind === 'all') guide = '한자 ' + KZN + '자 전체 회독 완료. 시험까지 이 장 반복으로 굳히세요.';",
    "  if (c.kind === 'all') guide = '한자 ' + (c.core ? c.b : KZN) + '자 ' + (c.core ? '' : '전체 ') + '회독 완료. 시험까지 이 장 반복으로 굳히세요.';")
