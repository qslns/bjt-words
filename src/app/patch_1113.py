# 11/13 — 홈 정리(확장 P1): 단어가 늘어도 홈이 길어지지 않게
# - 큰 접기 3개: '0부 · 기본'(data-g 'B') / 'BJT 단어'('P') / '한자'('kz', 그대로)
#   머리: 이름 · 범위 · 끝낸 장 n/m(그 묶음의 모든 장) · 진행중
# - 큰 접기 안: 500개 묶음마다 작은 접기(기본 n: 'b0'…, n부 · 이름: 'p0'…) + 맨 아래 총정리 카드(기본 전체 총정리 / 전체 총정리)
#   → 접힌 홈에는 장 카드가 하나도 안 보임(전에는 총정리 카드 2장이 접기 밖에 있었음)
# - 펼침 기억은 그대로 GOPEN(앱 쓰는 동안만). 큰 접기를 닫았다 열어도 안쪽 묶음 펼침은 그대로
# - 시험일이 지났으면 머리의 'D+n' 대신 작은 '시험일?' → 누르면 설정의 시험일 칸으로
# - 장 키·진도·이어서 하기·약점·목록·통계는 안 건드림

# ---------- CSS ----------
rep(".gf>.g-in{padding:2px 14px 16px;display:flex;flex-direction:column;gap:10px}",
    ".gf>.g-in{padding:2px 14px 16px;display:flex;flex-direction:column;gap:10px}\n"
    "/* 11/13: 큰 접기 안의 500개 묶음 접기 */\n"
    ".gf .gf{border-radius:10px}\n"
    ".gf .gf>summary{min-height:50px;padding:8px 14px}\n"
    ".gf .gf>summary b{font-size:16px}\n"
    ".gf .gf>.g-in{padding:2px 12px 14px}\n"
    ".dchip.dq{font-size:13px;font-weight:600;padding:3px 10px;color:var(--ink-2);border:1px dashed var(--ink-3);background:transparent}\n"
    ".dchip.dq:active{background:var(--surface-2)}\n"
    "/* 휴대폰 폭: 머리 '+ 기본 N'이 시험일 칩 밑으로 겹쳐 그려지던 것(전부터) → 좁은 화면에선 숨김(아이패드는 그대로) */\n"
    "@media (max-width:480px){.brand .b-sub2{display:none}}")
# 접기 표시(펼치기 + / 접기 −)는 자기 접기 상태만 따름: 큰 접기가 열려 있어도 닫힌 안쪽 접기는 '펼치기 +'
rep('.gf[open] .fold::after{content:"접기 −"}', '.gf[open]>summary .fold::after{content:"접기 −"}')
rep(".kzu-ph{font-size:13px;font-weight:600;color:var(--ink-2);margin-top:4px}",
    ".kzu-ph,.g-ph{font-size:13px;font-weight:600;color:var(--ink-2);margin-top:4px}")

# ---------- 머리: 시험일이 지났으면 '시험일?' ----------
rep("  const ddTxt = D > 0 ? 'D-' + D : D === 0 ? 'D-DAY' : 'D+' + (-D);\n",
    "  const ddTxt = D > 0 ? 'D-' + D : 'D-DAY';\n")
rep("""      '<span class="dchip" title="' + (exD.getUTCMonth() + 1) + '/' + exD.getUTCDate() + '(' + WD[exD.getUTCDay()] + ') 시험">' + ddTxt + '</span><div class="grow"></div>' +""",
    """      (D < 0 ? '<button class="dchip dq" data-act="examSet" aria-label="다음 시험일 정하기">시험일?</button>'
        : '<span class="dchip" title="' + (exD.getUTCMonth() + 1) + '/' + exD.getUTCDate() + '(' + WD[exD.getUTCDay()] + ') 시험">' + ddTxt + '</span>') + '<div class="grow"></div>' +""")
rep("    case 'settings': openSettings(); break;\n",
    "    case 'settings': openSettings(); break;\n"
    "    case 'examSet': { openSettings(); const x = $('#exam-date'), sb = $('#sheet-body'); if (x && sb) { const sec = x.closest('section') || x; sb.scrollTop = Math.max(0, sec.getBoundingClientRect().top - sb.getBoundingClientRect().top + sb.scrollTop - 8); } break; }\n")
rep('<p class="hint">홈의 D-day가 이 날짜 기준이에요.</p>',
    '<p class="hint">홈의 D-day가 이 날짜 기준이에요. 날짜가 지나면 홈에 ‘시험일?’로 보여요.</p>')

# ---------- 홈: 큰 접기 3개 ----------
rep("/* 홈의 큰 묶음(0부·1부…)은 접어 두고 눌러서 펼침. 펼친 묶음은 앱을 쓰는 동안 기억(홈을 다시 그려도 유지) */",
    "/* 홈의 묶음은 접어 두고 눌러서 펼침: 큰 접기(기본 B · BJT 단어 P · 한자 kz) 안에 500개 묶음 접기(b0… · p0…).\n"
    "   펼친 묶음은 앱을 쓰는 동안 기억(홈을 다시 그려도 유지, 큰 접기를 닫아도 안쪽 펼침은 그대로) */")
rep("""function basicHTML() {
  if (!BTOTAL) return '';
  const cs = CHAPTERS.filter(c => c.basic), parts = [];
  cs.forEach(c => { if (c.kind !== 'all') (parts[c.part] = parts[c.part] || []).push(c); });
  const allc = cs.find(c => c.kind === 'all');
  return parts.map((ps, p) => {
    const a = p * 500 + 1, b = Math.min(BTOTAL, a + 499);
    return foldHTML('b' + p, 'grp-basic', '0부 · 기본' + (parts.length > 1 ? ' ' + (p + 1) : ''), '기본 ' + a + '–' + b, ps,
      (p === 0 ? '<p class="part-h">N5·N4 단어 중 BJT에 나오는 기초 단어 · 1500 단어와 겹치는 건 같은 카드 · 250개씩 50개 단위로 쌓아 가며 회독</p>' : '') +
      '<div class="books">' + ps.map(c => bookHTML(c)).join('') + '</div>');
  }).join('') + (allc ? '<section class="grp grp-basic"><div class="grp-h"><b>기본 전체 총정리</b><span>기본 1–' + BTOTAL + '</span><i class="rule"></i></div><div class="books">' + bookHTML(allc) + '</div></section>' : '');
}
function partsHTML() {
  const parts = [];
  for (const c of CHAPTERS) { if (c.kind === 'all' || c.basic) continue; (parts[c.part] = parts[c.part] || []).push(c); }
  const lab = ['핵심', '중요', '확장', '보충', '보충', '보충'];
  let out = parts.map((cs, p) => {
    const a = p * 500 + 1, b = Math.min(TOTAL, a + 499);
    return foldHTML('p' + p, '', (p + 1) + '부 · ' + (lab[p] || '보충'), 'No.' + a + '–' + b, cs,
      '<p class="part-h">250개씩 50개 단위로 쌓아 가며 회독 → 마지막 장은 ' + a + '–' + b + ' 총정리</p>' +
      '<div class="books">' + cs.map(c => bookHTML(c)).join('') + '</div>');
  }).join('');
  const all = CHAPTERS.find(c => c.kind === 'all' && !c.basic);
  if (all) out += '<section class="grp"><div class="grp-h"><b>전체 총정리</b><span>No.1–' + TOTAL + '</span><i class="rule"></i></div><div class="books">' + bookHTML(all) + '</div></section>';
  return out;
}""", """/* 큰 접기 하나: 머리(이름·범위·그 묶음 모든 장의 끝낸 장·진행중) + 안내 한 줄 + 500개 묶음 작은 접기들 + 맨 아래 총정리 카드 */
function bigFoldHTML(key, cls, title, range, note, cs, sub, allName) {
  const parts = [];
  cs.forEach(c => { if (c.kind !== 'all') (parts[c.part] = parts[c.part] || []).push(c); });
  const all = cs.find(c => c.kind === 'all');
  const inner = '<p class="part-h">' + note + '</p>' +
    parts.map((ps, p) => { const s = sub(p); return foldHTML(s.key, cls, s.title, s.range, ps, '<div class="books">' + ps.map(c => bookHTML(c)).join('') + '</div>'); }).join('') +
    (all ? '<p class="g-ph">' + allName + '</p><div class="books">' + bookHTML(all) + '</div>' : '');
  return foldHTML(key, cls, title, range, cs, inner);
}
function basicHTML() {
  if (!BTOTAL) return '';
  const cs = CHAPTERS.filter(c => c.basic);
  return bigFoldHTML('B', 'grp-basic', '0부 · 기본', '기본 1–' + BTOTAL, 'N5·N4 기초 단어 · BJT 단어와 겹치는 건 같은 카드 · 250개씩 50개 단위로 쌓아 가며 회독', cs,
    p => ({key: 'b' + p, title: '기본 ' + (p + 1), range: '기본 ' + (p * 500 + 1) + '–' + Math.min(BTOTAL, p * 500 + 500)}), '기본 전체 총정리');
}
function partsHTML() {
  const cs = CHAPTERS.filter(c => !c.basic);
  if (!cs.length) return '';
  const lab = ['핵심', '중요', '확장', '보충', '보충', '보충', '보충', '보충'];
  return bigFoldHTML('P', 'grp-main', 'BJT 단어', 'No.1–' + TOTAL, '번호가 앞일수록 BJT 핵심 · 250개씩 50개 단위로 쌓아 가며 회독 · 500개마다 총정리', cs,
    p => ({key: 'p' + p, title: (p + 1) + '부 · ' + (lab[p] || '보충'), range: 'No.' + (p * 500 + 1) + '–' + Math.min(TOTAL, p * 500 + 500)}), '전체 총정리');
}""")
