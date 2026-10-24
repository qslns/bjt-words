# ================= 10/15 편의성 패치: 소리 반응 · 화면 밀림 · 버튼 자리 고정 · 홈 스크롤 기억 =================
# patch_app.py 끝에서 patch_1015.py 다음에 exec 로 실행됨

CSS_1015B = r'''
/* ---------- 10/15 편의성 ---------- */
/* 화면 전체가 출렁이며 밀리는 것 줄이기(레이아웃·터치는 그대로) */
html,body{overscroll-behavior:none}
[data-act]{touch-action:manipulation}
/* 공부 화면 글자는 길게 눌러도 선택·복사 메뉴가 안 뜨게(스크롤하다 잘못 잡히는 것 방지) */
.stage,.sheet-stage{-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}
/* 아래 버튼 자리 고정: 앞면 [해설][모르겠음][알고있음] · 해설 [발음][모르겠음][알고있음] · 모름 [발음][다음 →] */
#v-study .abar-in{display:grid;grid-template-columns:repeat(3,minmax(0,360px));justify-content:center}
#v-study .ab{max-width:none;min-width:0}
#v-study .ab-next{grid-column:span 2;max-width:none}
.ab-gap{display:block}
.ans-hw[data-act]{cursor:pointer;-webkit-user-select:none;user-select:none}
'''
rep('</style>\n</head>', CSS_1015B + '</style>\n</head>')

# ---------- 소리: 메모리에 미리 받아 두고 바로 재생 ----------
rep("const AUD = {\n  on: IS_PWA,",
r"""/* 소리 빨리 내기: 지금 카드·다음 카드 소리를 미리 메모리(blob)에 받아 두고, 누르면 서비스워커를 거치지 않고 바로 재생 */
const AMEM = {
  m: new Map(), max: 60,
  take(url) { const e = this.m.get(url); if (!e || !e.u) return null; e.t = Date.now(); return e.u; },
  drop(url) { const e = this.m.get(url); if (!e) return; if (e.u) { try { URL.revokeObjectURL(e.u); } catch (x) {} } this.m.delete(url); },
  want(urls) {
    if (!AUD.on || typeof fetch !== 'function' || !window.URL || !URL.createObjectURL) return;
    for (const url of urls) {
      if (!url) continue;
      const e = this.m.get(url);
      if (e) { e.t = Date.now(); continue; }
      const n = {u: null, t: Date.now(), busy: true};
      this.m.set(url, n);
      fetch(url).then(r => r.ok ? r.blob() : null).then(b => {
        n.busy = false;
        if (this.m.get(url) !== n) return;
        if (!b || b.size < 200) { this.m.delete(url); return; }
        if (!b.type) b = new Blob([b], {type: 'audio/mpeg'});
        n.u = URL.createObjectURL(b);
      }).catch(() => { n.busy = false; if (this.m.get(url) === n) this.m.delete(url); });
    }
    this.trim();
  },
  trim() {
    if (this.m.size <= this.max) return;
    const cur = AUD.el ? AUD.el.src : '';
    const old = [...this.m.entries()].sort((a, b) => a[1].t - b[1].t);
    for (const [k, e] of old) {
      if (this.m.size <= this.max) break;
      if (e.busy || (e.u && e.u === cur)) continue;
      this.drop(k);
    }
  }
};
const AUD = {
  on: IS_PWA, btn: null,""")
rep("""      try { a.preservesPitch = true; a.webkitPreservesPitch = true; } catch (e) {}
      this.el = a;""",
"""      try { a.preservesPitch = true; a.webkitPreservesPitch = true; } catch (e) {}
      this.el = a;""")
rep("""  play(url, fallback) {
    const a = this.get();
    const token = ++this.seq;
    const failOnce = () => { if (token !== this.seq) return; this.seq++; this.fail(fallback); };
    TTS.stop();
    try { a.pause(); } catch (e) {}
    a.onerror = failOnce;
    a.src = url;
    const r = S.rate || 1;
    try { a.defaultPlaybackRate = r; a.playbackRate = r; } catch (e) {}
    let p;
    try { p = a.play(); } catch (e) { failOnce(); return; }
    if (p && p.catch) p.catch(err => { const n = err && err.name; if (n === 'AbortError' || n === 'NotAllowedError') return; failOnce(); });
  },""",
"""  play(url, fallback, btn) {
    const a = this.get();
    const token = ++this.seq;
    const mem = AMEM.take(url);
    let direct = !mem;
    const failOnce = () => {
      if (token !== this.seq) return;
      if (!direct) { direct = true; AMEM.drop(url); start(url); return; }   /* 메모리 소리가 안 되면 주소로 한 번 더 */
      this.seq++; this.fail(fallback);
    };
    const start = src => {
      try { a.pause(); } catch (e) {}
      a.onerror = failOnce;
      if (a.src === src && a.readyState >= 2) { try { a.currentTime = 0; } catch (e) { a.src = src; } }   /* 같은 소리 다시: 되감기만 */
      else a.src = src;
      const r = S.rate || 1;
      try { a.defaultPlaybackRate = r; a.playbackRate = r; } catch (e) {}
      let p;
      try { p = a.play(); } catch (e) { failOnce(); return; }
      if (p && p.catch) p.catch(err => { const n = err && err.name; if (n === 'AbortError') return; if (n === 'NotAllowedError') return; failOnce(); });
    };
    TTS.stop();
    start(mem || url);
    if (!mem) AMEM.want([url]);   /* 다음에 누를 땐 바로 */
  },
  mark() {},""")
rep("  stop() { this.seq++; if (this.el) { try { this.el.pause(); } catch (e) {} } },",
    "  stop() { this.seq++; if (this.el) { try { this.el.pause(); } catch (e) {} } },")
rep("const sayWord = id => { const w = byId.get(id); if (!w) return; const t = w.tw || w.r; if (AUD.on) AUD.play(AUD.url('w', id), t); else TTS.say(t); };",
    "const sayWord = (id, btn) => { const w = byId.get(id); if (!w) return; const t = w.tw || w.r; if (AUD.on) AUD.play(AUD.url('w', id), t, btn); else TTS.say(t); };")
rep("const saySent = (id, i) => { const w = byId.get(id); if (!w || !w.e[i]) return; if (AUD.on) AUD.play(AUD.url('s', id, i), w.e[i].t); else TTS.say(w.e[i].t); };",
    "const saySent = (id, i, btn) => { const w = byId.get(id); if (!w || !w.e[i]) return; if (AUD.on) AUD.play(AUD.url('s', id, i), w.e[i].t, btn); else TTS.say(w.e[i].t); };")
rep("""function warmCard(id, all) {
  if (!AUD.on) return;
  const w = byId.get(id); if (!w) return;
  if (all) AUD.warm(w.e.map((e, i) => AUD.url('s', id, i)));
  else AUD.warm([AUD.url('w', id), AUD.url('s', id, frontSentIdx(w, getRun()))]);
}""",
"""function warmCard(id, all) {
  if (!AUD.on) return;
  const w = byId.get(id); if (!w) return;
  if (all) { AMEM.want([AUD.url('w', id)].concat(w.e.map((e, i) => AUD.url('s', id, i)))); return; }
  const r = getRun();
  AMEM.want([AUD.url('w', id), AUD.url('s', id, frontSentIdx(w, r))]);
  /* 다음 카드 소리도 미리: 알고있음을 누르자마자 나오게 */
  const nx = r ? (r.ph === 'main' ? r.ord[r.pos + 1] : r.q[r.qpos + 1]) : null, nw = nx != null ? byId.get(nx) : null;
  if (nw) AMEM.want([AUD.url('w', nx), AUD.url('s', nx, frontSentIdx(nw, r))]);
}""")
rep("  if (AUD.on) AUD.warm([AUD.url('w', id), AUD.url('s', id, 0)].concat(ORDER[H.lt.pos + 1] != null ? [AUD.url('w', ORDER[H.lt.pos + 1])] : []));",
    "  if (AUD.on) AMEM.want([AUD.url('w', id), AUD.url('s', id, 0)].concat(ORDER[H.lt.pos + 1] != null ? [AUD.url('w', ORDER[H.lt.pos + 1])] : []));")
rep("""  else { const w = byId.get(en.id); if (!w) { closeSheet(); return; } openSheet('<span lang="ja">' + esc(w.w) + '</span>', '<div class="sheet-stage' + modeCls() + '">' + explainHTML(w, true) + '</div>'); }""",
    """  else { const w = byId.get(en.id); if (!w) { closeSheet(); return; } openSheet('<span lang="ja">' + esc(w.w) + '</span>', '<div class="sheet-stage' + modeCls() + '">' + explainHTML(w, true) + '</div>'); if (AUD.on) AMEM.want([AUD.url('w', w.id), AUD.url('s', w.id, 0)]); }""")
rep("    case 'sayW': { const id = idAttr != null ? idAttr : ui.id; if (id != null) sayWord(id); break; }\n"
    "    case 'sayS': if (idAttr != null) saySent(idAttr, +el.dataset.i || 0); break;\n"
    "    case 'saySF': { if (ui.id == null) break; const w = byId.get(ui.id); saySent(ui.id, frontSentIdx(w, getRun())); break; }\n",
    "    case 'sayW': { const id = idAttr != null ? idAttr : ui.id; if (id != null) sayWord(id, el); break; }\n"
    "    case 'sayS': if (idAttr != null) saySent(idAttr, +el.dataset.i || 0, el); break;\n"
    "    case 'saySF': { if (ui.id == null) break; const w = byId.get(ui.id); saySent(ui.id, frontSentIdx(w, getRun()), el); break; }\n")

# ---------- 해설의 큰 단어도 누르면 발음 ----------
rep("""    '<div class="ans-row"><h2 class="ans-hw' + ([...w.w].length >= 10 ? ' xlong' : [...w.w].length >= 6 ? ' long' : '') + '" lang="ja">' + headRuby(w) + '</h2>'""",
    """    '<div class="ans-row"><h2 class="ans-hw' + ([...w.w].length >= 10 ? ' xlong' : [...w.w].length >= 6 ? ' long' : '') + '" lang="ja"' + (CAN_SPEAK() ? ' data-act="sayW" data-id="' + w.id + '" role="button" tabindex="0" aria-label="' + esc(w.w) + ' 발음 듣기"' : '') + '>' + headRuby(w) + '</h2>'""")

# ---------- 아래 버튼 자리 고정 ----------
rep("""  if (ui.mode === 'unknown') bar = '<button class="ab ab-next" data-act="next">다음 →</button>';
  else if (ui.rev) bar = '<button class="ab ab-ng" data-act="ng">' + ICON.q + '모르겠음</button><button class="ab ab-ok" data-act="ok">' + ICON.check + '알고있음</button>';""",
"""  const sayB = CAN_SPEAK() ? '<button class="ab ab-ex ab-say" data-act="sayW" aria-label="발음 다시 듣기">' + ICON.spk + '발음</button>' : '<span class="ab-gap"></span>';
  if (ui.mode === 'unknown') bar = sayB + '<button class="ab ab-next" data-act="next">다음 →</button>';
  else if (ui.rev) bar = sayB + '<button class="ab ab-ng" data-act="ng">' + ICON.q + '모르겠음</button><button class="ab ab-ok" data-act="ok">' + ICON.check + '알고있음</button>';""")

# ---------- 홈 스크롤 위치 기억: 장을 하고 돌아오면 보던 자리 그대로 ----------
rep("""function show(v) {
  view = v;""",
"""const SCR = {};   /* 홈 스크롤 위치(홈을 다시 그려도·다른 화면 갔다 와도 그대로) */
function show(v) {
  view = v;""")
rep("""      '<p class="ver">앱 버전 ' + BUILD + ' · 단어 ' + TOTAL.toLocaleString() + '개' + (BTOTAL ? ' + 기본 ' + BTOTAL + '개' : '') + '</p>' +
    '</div></div>';
}""",
"""      '<p class="ver">앱 버전 ' + BUILD + ' · 단어 ' + TOTAL.toLocaleString() + '개' + (BTOTAL ? ' + 기본 ' + BTOTAL + '개' : '') + '</p>' +
    '</div></div>';
  { const sc = V.home.querySelector('.scroll'); if (sc) { if (SCR.home) sc.scrollTop = SCR.home; sc.addEventListener('scroll', () => { SCR.home = sc.scrollTop; }, {passive: true}); } }
}""")
rep("window.__t = {get ui() { return ui; }, CHAPTERS, AUD, AV, AVH, audioPrune,",
    "window.__t = {get ui() { return ui; }, CHAPTERS, AUD, AMEM, AV, AVH, audioPrune, storyHTML, kpHTML,")
