# 10/21 — 단어 공부·한자 단원 위 막대에 [후리가나] 켜기/끄기(사용자 요청: 설정까지 안 가고 단어 넘기면서 바로)
# - 설정의 '후리가나 항상/탭해서'(S.furi 'all'|'tap')와 같은 값. 끄면 예문 후리가나(누르면 그 문장만 보임) + 같은 한자 단어·한자 카드 단어 목록 후리가나를 숨김
# - 답(해설 맨 위 단어의 읽기·후리가나)과 한자 칸 읽기는 그대로 보임(맞는지 확인용)
# - 화면을 다시 그리지 않고 클래스만 바꿈(스크롤 위치 그대로)

FURI_BTN = """'<button class="tb furi" data-act="furi" aria-pressed="' + (S.furi !== 'tap') + '" aria-label="후리가나 ' + (S.furi !== 'tap' ? '끄기' : '켜기') + '"><span class="furi-ic" lang="ja" aria-hidden="true">あ</span><span class="sm-hide">후리가나</span></button>' +"""
# 단어 공부 막대: [소리] 다음, [이전] 앞
rep("""    '<button class="tb" data-act="undo" aria-label="이전 카드로 되돌리기"' + (undoStack.length ? '' : ' disabled') + '>' + ICON.undo + '<span class="sm-hide">이전</span></button>' +""",
    "    " + FURI_BTN + """
    '<button class="tb" data-act="undo" aria-label="이전 카드로 되돌리기"' + (undoStack.length ? '' : ' disabled') + '>' + ICON.undo + '<span class="sm-hide">이전</span></button>' +""")
# 한자 단원 막대: [이전] 앞
rep("""    '<button class="tb" data-act="kzUndo" aria-label="이전 카드로 되돌리기"' + (kundo.length ? '' : ' disabled') + '>' + ICON.undo + '<span class="sm-hide">이전</span></button>' +""",
    "    " + FURI_BTN + """
    '<button class="tb" data-act="kzUndo" aria-label="이전 카드로 되돌리기"' + (kundo.length ? '' : ' disabled') + '>' + ICON.undo + '<span class="sm-hide">이전</span></button>' +""")
# 한자 단원 화면도 후리가나 모드 클래스
rep("""    '<div class="scroll" id="kz-sc"><div class="stage" id="kz-stage">' + body + '</div></div>' +""",
    """    '<div class="scroll" id="kz-sc"><div class="stage' + modeCls() + '" id="kz-stage">' + body + '</div></div>' +""")
rep("""function refreshStage() {
  const st = $('#stage'); if (st) st.className = 'stage' + modeCls();
  const sb = $('#sheet-body .sheet-stage'); if (sb) sb.className = 'sheet-stage' + modeCls();
}""", """function refreshStage() {
  const st = $('#stage'); if (st) st.className = 'stage' + modeCls();
  const sb = $('#sheet-body .sheet-stage'); if (sb) sb.className = 'sheet-stage' + modeCls();
  const ks = $('#kz-stage'); if (ks) ks.className = 'stage' + modeCls();
  document.querySelectorAll('[data-act="furi"]').forEach(b => { const on = S.furi !== 'tap'; b.setAttribute('aria-pressed', on); b.setAttribute('aria-label', '후리가나 ' + (on ? '끄기' : '켜기')); });
}""")
# 버튼 동작
rep("    case 'setFuri': setS({furi: el.dataset.v}); openSettings(); refreshStage(); break;\n",
    "    case 'setFuri': setS({furi: el.dataset.v}); openSettings(); refreshStage(); break;\n"
    "    case 'furi': setS({furi: S.furi === 'tap' ? 'all' : 'tap'}); refreshStage(); toast(S.furi === 'tap' ? '후리가나 숨김 · 예문은 누르면 보여요' : '후리가나 보임'); break;\n")
# 설정 이름도 같은 뜻으로
rep("segB('setFuri', S.furi, [['all', '후리가나 항상'], ['tap', '후리가나 탭해서']])",
    "segB('setFuri', S.furi, [['all', '후리가나 보임'], ['tap', '후리가나 숨김(예문 누르면 보임)']])")
# 숨김일 때: 같은 한자 단어·한자 카드 단어 목록 후리가나도 숨김(답 단어와 한자 칸 읽기는 그대로)
rep(".furi-off .sent:not(.peek) .jp rt{visibility:hidden}",
    ".furi-off .sent:not(.peek) .jp rt{visibility:hidden}\n.furi-off .sk-j rt{visibility:hidden}\n"
    ".tb.furi .furi-ic{font-family:var(--f-jp);font-size:19px;font-weight:700;line-height:1;width:21px;text-align:center}\n"
    ".tb.furi[aria-pressed=\"false\"] .furi-ic{text-decoration:line-through;text-decoration-thickness:2px;opacity:.55}")
