# 10/20 — 한자 소리(사용자 요청: 한자 먼저 1회독, 한자를 보면 읽기가 바로 나오게)
# - 대표 소리 audio/k/<한자 코드>.mp3: 훈독이 더 중요한 한자는 [1순위 훈독 → 음독], 나머지는 음독(중요 순, 흘려보기 뺌) — kz/kz_imp.py의 rep
# - 읽기마다 소리 audio/kr/<읽기 코드>.mp3: 한자 카드 머리의 읽기 칩(①②③)을 누르면 그 읽기(단어 카드에서 여는 한자 카드도 같음)
# - 앞면: 단어장처럼 큰 한자를 누르면 대표 소리(자동 재생 없음) · 해설/모름: S.auto(해설에서 자동 발음)면 한 번 + 아래 빈자리 [발음]
# - 다음 카드로 넘어가면 소리 멈춤, 이번 카드 대표 소리를 메모리에 미리 받아 둠 · 음성 전체 받아두기·옛 음성 정리에 한자 소리 포함

rep("function kzRender() {\n  const r = kzRun(), c = kui.c;\n",
"""/* 10/20 한자 소리: 파일이 있는 것만(av에 k/·kr/ 키, 주소에 ?v=해시). 없거나 앱 음성이 꺼져 있으면 기기 음성 */
const kzPlain = r => String(r == null ? '' : r).replace(/[()（）]/g, '');
const kzRepKey = c => 'k/' + String(c).codePointAt(0).toString(16);
const kzRdKey = r => 'kr/' + [...kzPlain(r)].map(ch => ch.codePointAt(0).toString(16)).join('-');
const kzAUrl = k => new URL('audio/' + k + '.mp3' + (AV[k] ? '?v=' + AV[k] : ''), location.href).href;
function kzSayText(c) {
  const k = KC[c]; if (!k) return '';
  const rp = Array.isArray(k.rep) && k.rep.length ? k.rep : (Array.isArray(k.on) ? k.on : []).filter(x => !/っ$/.test(x));
  return rp.map(kzPlain).filter(Boolean).join('、');
}
function sayKanji(c, btn) {
  const t = kzSayText(c); if (!t) return;
  const k = kzRepKey(c);
  if (AUD.on && AV[k]) AUD.play(kzAUrl(k), t, btn); else TTS.say(t);
}
function sayReading(r, btn) {
  const p = kzPlain(r); if (!p || /っ$/.test(p)) return;
  const k = kzRdKey(p);
  if (AUD.on && AV[k]) AUD.play(kzAUrl(k), p, btn); else TTS.say(p);
}
const kzSayB = c => CAN_SPEAK() && kzSayText(c) ? '<button class="ab ab-ex ab-say" data-act="kzSay" aria-label="발음 다시 듣기">' + ICON.spk + '발음</button>' : '<span class="ab-gap"></span>';
function kzWarm(c) { try { const k = kzRepKey(c); if (AUD.on && AV[k]) AMEM.want([kzAUrl(k)]); } catch (e) { /* 미리 받기 실패는 무시 */ } }
function kzRender() {
  const r = kzRun(), c = kui.c;
""")
rep("""  const gap = '<span class="ab-gap"></span>';   /* 소리 버튼 자리: 비워서 버튼 자리 고정 */""",
    """  const gap = kzSayB(c);   /* 10/20 [발음](소리를 못 내면 빈자리로 버튼 자리 고정) */""")
# 앞면: 큰 한자를 누르면 대표 소리(단어장 앞면과 같은 모양·안내)
rep("""    : kzTopHTML(c, r, false) + '<div class="cf-mid"><div class="cf-word w1 kzu-q" lang="ja">' + esc(c) + '</div></div>';""",
    """    : kzTopHTML(c, r, false) + '<div class="cf-mid"><button class="cf-word w1 kzu-q" data-act="kzSay" lang="ja" aria-label="' + esc(c) + ' 발음 듣기">' + esc(c) + '</button>' +
      (CAN_SPEAK() && kzSayText(c) ? '<span class="cf-hint">' + ICON.spk + '한자를 누르면 발음</span>' : '') + '</div>';""")
# 해설 열 때 자동 발음(단어 공부 showExplain과 같음)
rep("""function kzExplain() {
  if (!kctx || kui.rev) return;
  kui.rev = true; kui.mode = 'explain'; kui.lock = mono() + 300;
  kzRender();
}""", """function kzExplain() {
  if (!kctx || kui.rev) return;
  kui.rev = true; kui.mode = 'explain'; kui.lock = mono() + 300;
  kzRender();
  if (S.auto) sayKanji(kui.c);
}""")
# 앞면에서 모르겠음 → 카드 + 자동 발음(단어 공부와 같음)
rep("""  if (!known && !kui.rev) {
    kui = {rev: true, mode: 'unknown', c, t0: m, lock: m + 300};
    kzRender();
    return;
  }
  kzEnter();
}""", """  if (!known && !kui.rev) {
    kui = {rev: true, mode: 'unknown', c, t0: m, lock: m + 300};
    kzRender();
    if (S.auto) sayKanji(c);
    return;
  }
  kzEnter();
}""")
# 다음 한자로 넘어갈 때 소리 멈추고 이번 한자 대표 소리를 미리 받아 둠
rep("""  const m = mono();
  closeModal();
  kui = {rev: false, mode: 'front', c, t0: m, lock: m + 300};
  kzRender();
}""", """  const m = mono();
  closeModal(); stopVoice();
  kui = {rev: false, mode: 'front', c, t0: m, lock: m + 300};
  kzRender();
  kzWarm(c);
}""")
rep("function kzExit() { kctx = null; show('home');", "function kzExit() { stopVoice(); kctx = null; show('home');")
# 버튼 동작: 대표 소리(앞면 한자·[발음]) / 읽기 칩(한자 카드 어디서든)
rep("case 'kzExplain': kzExplain(); break;\n",
    "case 'kzExplain': kzExplain(); break;\n    case 'kzSay': { const c = el.dataset.c || (kctx && kui.c); if (c) sayKanji(c, el); break; }\n    case 'kzRd': sayReading(el.dataset.r, el); break;\n")
# 음성 전체 받아두기·옛 음성 정리에 한자 소리 포함
rep("const AUDIO_TOTAL = W.reduce((n, w) => n + 1 + w.e.length, 0);",
    "const AUDIO_TOTAL = W.reduce((n, w) => n + 1 + w.e.length, 0) + Object.keys(DATA.av || {}).filter(k => /^kr?\\//.test(k)).length;   /* 10/20 한자 소리 포함 */")
rep("'단어·예문 ' + AUDIO_TOTAL.toLocaleString() + '개를", "'단어·예문·한자 읽기 ' + AUDIO_TOTAL.toLocaleString() + '개를")
rep("function audioUrls() { const out = []; for (const id of ALL_IDS) { const w = byId.get(id); out.push(AUD.url('w', id)); w.e.forEach((e, i) => out.push(AUD.url('s', id, i))); } return out; }",
    "function audioUrls() { const out = []; for (const id of ALL_IDS) { const w = byId.get(id); out.push(AUD.url('w', id)); w.e.forEach((e, i) => out.push(AUD.url('s', id, i))); } for (const k of Object.keys(AV)) if (/^kr?\\//.test(k)) out.push(kzAUrl(k)); return out; }")
rep("    const m = /\\/audio\\/(w\\/\\d+|s\\/\\d+-\\d+)\\.mp3$/.exec(u.pathname);",
    "    const m = /\\/audio\\/(w\\/\\d+|s\\/\\d+-\\d+|k\\/[0-9a-f]+|kr\\/[0-9a-f-]+)\\.mp3$/.exec(u.pathname);")
# 시험용
rep("KC, KZO, KZCH, kzBodyHTML, kzRun,", "KC, KZO, KZCH, kzBodyHTML, kzRun, kzAUrl, kzRepKey, kzRdKey, kzSayText,")
