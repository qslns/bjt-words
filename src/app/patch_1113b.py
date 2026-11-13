# 11/13 — 다음 BJT: 2027년 2월 중후반(사용자, 날짜는 아직 미정) → 앱 시험일 기본값 2027-02-20
# - 저장된 시험일이 이미 지났으면(예전 기본값 10/22 등) 한 번만 2027-02-20으로 옮김(em 4). 앞날로 정해 둔 게 있으면 그대로
# - em 4를 저장값으로 인정(안 그러면 열 때마다 다시 옮겨 버림)
rep("const DEF_EXAM = '2026-10-22';", "const DEF_EXAM = '2027-02-20';")
rep("  if (o.em === 1 || o.em === 2 || o.em === 3) r.em = o.em;", "  if ([1, 2, 3, 4].includes(o.em)) r.em = o.em;")
rep("if (!(S.em >= 3)) { if (S.exam === '2026-10-13') S.exam = '2026-10-22'; S.em = 3; LS.set(KS, S); }\n",
    "if (!(S.em >= 3)) { if (S.exam === '2026-10-13') S.exam = '2026-10-22'; S.em = 3; LS.set(KS, S); }\n"
    "/* 11/13: 다음 BJT는 2027년 2월 중후반 → 지난 시험일이면 2/20으로 한 번만(날짜가 정해지면 설정 › 시험일) */\n"
    "if (!(S.em >= 4)) { const v = parseDay(S.exam); if (v == null || v < calDay(Date.now())) S.exam = DEF_EXAM; S.em = 4; LS.set(KS, S); }\n")
