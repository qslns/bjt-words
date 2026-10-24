# 앱 작업 지침: 한자칸 · 한자 카드 · 한자 단원 (BJT 단어 회독 PWA)

사용자는 이 앱으로 매일 시험(10/22) 단어를 외운다. **배포 뒤 오류로 공부를 못 하는 상황은 절대 안 됨**(사용자 직접 요구). 기존 단어 공부 흐름·기록은 한 글자도 깨지면 안 된다. 너는 구현과 시험까지만 한다 — 배포(git push)·저장소(/home/claude/bjt-words) 손대기 금지.

## 빌드 구조 (먼저 읽기)
- `/home/claude/work/app/app.tpl.html` = 원본 틀. `patch_app.py`가 `rep(old, new)`(정확히 1번 일치해야 함)로 고쳐 `app2.tpl.html`을 만든다. 끝에서 `patch_1015.py`, `patch_1015b.py`를 exec. **너는 `patch_1016.py`를 새로 만들고 patch_app.py 맨 끝(1015b 다음, 쓰기 직전)에 exec 한 줄만 추가.** 다른 patch 파일은 고치지 말 것(필요하면 1016에서 rep로 덮기).
- 빌드: `cd /home/claude/work/app && python3 patch_app.py && cd /home/claude/work && python3 app/make.py build/data_app.json app/test pwa https://qslns.github.io/bjt-words/ 120`
- 시험 서버: 이미 127.0.0.1:8765 에서 app/test 를 서빙 중이면 그대로, 아니면 `cd /home/claude/work/app/test && setsid nohup python3 -m http.server 8765 --bind 127.0.0.1 >/dev/null 2>&1 &`
- 시험: `cd /home/claude/work/app && DATA=/home/claude/work/build/data_app.json node test_app.mjs`, `node fs_test.mjs`, `node swupdate_test.mjs` — 지금 전부 통과 상태(133 / 9 / PASS). 끝날 때도 전부 통과해야 하고, 새 기능 시험을 test_app.mjs에 추가한다(기존 시험은 지우지 말고, 바뀐 기능에 맞게만 고침).
- 앱 안 주요 코드(app2.tpl.html 기준): `storyHTML`(이야기 칸), `kpHTML`(한자·부수 풀이 접는 칸), `skHTML`(같은 한자), `explainHTML`·`ansHTML`(해설), 시트: `openSheet`·`sheetShow`·`openWord`·`sheetStack`·`sheetBack`(이미 단어→단어 뒤로가기 있음), 클릭 처리 `case 'open'` 근처(`data-act`), 홈 `renderHome`·`foldHTML`(접는 묶음, patch_1015.py), 장 `CHAPTERS`·`genChapters`·`getRun`·`H`(기록)·`isWeak`(약점).

## 한자 카드 자료
- 카드 원본: `/home/claude/work/kz/gold.json`, `/home/claude/work/kz/batches/*.json`(지금 다른 작업이 950자를 채우는 중 — 일부만 있어도 동작해야 함).
- 컴파일: `cd /home/claude/work/kz && python3 kzc.py compile -o /home/claude/work/kz/kz_cards.json gold.json batches/*.json` → 카드 배열(형식은 kzc.py `compile_entry`). 그리는 함수는 `kz_render.js`(`kzCardHTML(card, {words})`), 모양은 `kz.css`. 미리보기 `preview.py`가 이 둘을 그대로 쓴다 → 앱에서도 같은 파일 내용을 그대로 넣어 쓸 것(복사본 만들지 말고 빌드 때 읽어 넣기).
- make.py: kz_cards.json이 있으면 `data.kc = {한자: 카드}`로 넣고, 한자 순서(많이 쓰는 순)는 `/home/claude/work/kanji_mn/kanji_src.json`의 순서로 `data.kzo = [한자…]`(950자 전부). 기존 `data.kanji`(b·bn·s·x 포함)는 그대로 둔다(카드 없는 한자의 대체 표시용). make.py 수정은 최소로.
- index.html 크기 늘어난 만큼 보고(지금 약 1.9MB).

## 1) 단어 카드: '이야기' 칸 → '한자' 칸
- 칸 이름 '이야기' → **'한자'**. 한자 줄 모양(왼쪽 네모 한자 + 오른쪽 글)은 지금처럼.
- 줄 내용: 첫 줄 = **훈음**(굵게) + 이 단어에서의 읽기(작게, 히라가나, `w.kr`에서) / 둘째 줄 = 카드의 **장면 한 줄(hook)**(`kzMark`로). 카드가 없는 한자는 지금처럼 '구성 + 풀이'(옛 자료) 그대로.
- 단어 전체 이야기 줄(`w.st`, '단어 → …')은 그대로 둔다.
- **'한자·부수 풀이' 접는 칸(kpHTML)은 단어 카드에서 완전히 뺀다**(해설 화면·시트 둘 다). 관련 설정(접어 두기/펼쳐 두기 같은 것)이 있으면 설정 화면에서도 빼되, 저장된 설정값이 남아 있어도 오류 없게.
- 한자칸의 네모 한자를 누르면(버튼) → **한자 카드 시트**. '같은 한자' 칸의 네모 한자(sk-k)도 누르면 한자 카드 시트.

## 2) 한자 카드 시트
- 같은 한자 칸의 단어를 눌렀을 때 단어 카드가 뜨는 것(`openWord` → `sheetStack`)과 **똑같은 방식**: `sheetStack.push({t:'kz', c})` → `sheetShow`에서 `t==='kz'`면 `openSheet(제목, 카드)`. 시트 밖(해설 화면 등)에서 누르면 새 스택으로 시작(지금 'open'과 같은 규칙), 시트 안에서 누르면 쌓이고 뒤로가기 버튼으로 돌아감.
- 내용 = `kzCardHTML(card, {words})`. **맨 아래 단어 목록**: 이 한자가 든 단어 전부(`data.kanji[c].u`, 본편 순서 → 기본 순서), 같은 한자 칸 단어와 비슷한 모양(단어 크게 + 읽기 + 짧은 뜻). 누르면 `data-act="open"`으로 단어 카드(같은 한자 칸에서 누를 때와 동일), 뒤로가기로 한자 카드로 돌아옴.
- 카드 없는 한자: 큰 한자 · 훈음 · 음독/훈독(히라가나) · 옛 구성/풀이 · 단어 목록으로 된 간단한 카드(오류 없이).
- 아이패드 가로(1180×820)·세로(820×1180)·휴대폰(390×844)에서 가로 넘침 없음.

## 3) 한자 단원 (기존 단어장과 같은 퀴즈)
- 홈에 접는 묶음 **'한자'**(foldHTML, 키 'kz'), 위치는 단어 묶음들(1–3부) 다음, 단어 목록 줄 위. 머리에 범위·'끝낸 장 n/총'.
- 장 구성: 단어와 같은 규칙(`genChapters`)을 950자(`data.kzo` 순서)에 적용 — 250개 안에서 50개씩 누적, 총정리.
- 공부 화면: 단어 공부 화면과 **같은 모양·같은 흐름**(앞면 → 해설 → 모르겠음/알고있음 → 다음, 라운드 반복·섞기 방식도 단어와 같게). 앞면 = 큰 한자 하나(단어장 글씨 `--f-kyo`), 해설 = 한자 카드(단어 목록 포함, 단어 누르면 단어 카드 시트). 소리 버튼 없음(그 자리는 비워 버튼 자리 고정 유지).
- 기록은 단어 기록과 **분리**(별도 키). 한자는 약점 단어·약점 수·단어 통계·'약점에 넣기'에 절대 섞이지 않게. 단어 장 진도·회독 수에도 영향 없게.
- 기존 단어 공부 코드를 재사용할지 따로 만들지는 너의 판단 — 단, 단어 공부 동작이 조금이라도 바뀌면 안 된다(기존 시험 전부 통과 + 단어 장 하나를 처음부터 끝까지 돌리는 시험으로 확인).

## 4) 시험 (test_app.mjs에 추가)
- 단어 카드(해설·시트): 칸 이름 '한자', 한자 줄 = 훈음 + hook, '한자·부수 풀이' 없음, 콘솔 오류 0.
- 한자칸 한자 누르기 → 한자 카드 시트 → 단어 누르기 → 단어 카드 → 뒤로 → 한자 카드 → 뒤로 → 원래 단어.
- 같은 한자 칸 네모 한자 누르기 → 한자 카드.
- 한자 단원: 홈 묶음 펼치기 → 첫 장 시작 → 앞면에 한자만 → 해설에 카드 → 알고있음/모르겠음 → 장 끝까지 → 기록 저장(새로고침 후 유지) → 약점 단어 수·단어 장 기록 변화 없음.
- 모든 카드(kz_cards.json 전부) 그려서 undefined/NaN 없음, 세 화면 크기에서 가로 넘침 없음(카드 몇 개 표본 + 한자 단원 화면).
- 기존 시험 전부 통과. fs_test·swupdate_test 통과.

## 마무리 보고
- 바꾼 파일 목록, patch_1016.py 요약, 시험 결과(숫자), index.html 크기, 판단이 필요했던 부분과 고른 방법, 걱정되는 점.
