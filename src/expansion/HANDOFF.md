# 단어장 확장 인계 (2026-11-13 작성)

앱: https://qslns.github.io/bjt-words/ · 저장소 `qslns/bjt-words` · **작업 브랜치 `expansion`** (main = 지금 배포본, 직접 커밋 금지)

이 문서를 받는 쪽은 처음부터 시작하는 세션이에요(사용자와 대화하는 새 페이지, 또는 3시간마다 도는 예약 작업). 이 대화를 모르니 아래만 믿고 진행해요.

**읽는 순서**: 이 문서 → `PROGRESS.md`(지금 어디까지, 잠금) → `CARD_SPEC.md`(카드 쓰는 법) → `LESSONS.md`(시행착오) → `src/README.md`(빌드·시험·배포 원래 방법).

---

## 1. 무엇을 왜 하나

다음 BJT(약 90~100일 뒤)에서 400을 확실히, 430을 높은 확률로 넘기려고 단어장을 넓혀요. 사용자는 하루 한 단원(50개)씩 늘리고 앞 단원은 250~500개 단위로 복습하다 거의 완벽해지면 약점만 보는 식으로 공부함. 시험과 상관없이 일본에서 살 계획이라 단어는 계속 볼 거고, 2027년 7월 JLPT N1도 이 단어장 단어만으로 볼 예정.

사용자가 정한 범위(11/11): "기초는 전부 다 넣고 … 지금 있는 800몇 개에 추가로 넣어서 기본 부분으로 만들고 나머지 bjt 추가본도 다 해서 넣을 거"
11/13: 홈이 길어지니 "−(접기)에 안 들어가는 500개씩 있는 거나 큰 것들도 같이 집어넣어서 훨씬 압축되고 정리되는 시스템"으로. "max 요금제를 다 써 버릴 생각이니 최대한 빡세게."

| 단계 | 내용 | 규모 | 사용자 확인 |
|---|---|---|---|
| P1 | 홈 정리: 기본·BJT·한자를 각각 큰 접기 하나로, 총정리 카드도 접기 안으로 | 패치 1개 + 시험 | 방향 승인(11/13) |
| P2 | 기본 추가: N5·N4 중 앱에 없는 말 → 기본 886번부터 | 약 470장 새로 | 승인 |
| P3 | 복원: 10/5에 지운 BJT 단어 2,312개 → 본편 1,501번부터(값 순서) | 2,312장 손보기 | 승인 |
| P4 | N3·N2 중 없는 말 약 1,300개 | — | **아직 안 물어봄 → 사용자 OK 전엔 앱에 넣지 말 것**(카드 초안을 따로 만들어 두는 건 괜찮음) |
| P5 | 새 한자(약 520자) 그림 카드 | 큼 | 안 물어봄. 그 전엔 단어 카드에서 옛 방식(구성·풀이)으로 보임 |

순서: P1 → P2 → P3(500개씩 끊어 배포) → (P4·P5는 확인 뒤). 사용자는 지금 BJT 250개·기본 500개를 본 상태라 기본 501~·BJT 1,501~는 몇 주 뒤에 필요함 → 서두르지 말고 **틀리지 않게**.

## 2. 절대 규칙

1. **공식 모의 문제집 내용은 어디에도 쓰지 않음.** 문장·지문·문항·정답을 카드·문서·커밋에 옮기지 않고, 단어 고르기·순서에도 안 씀(사용자가 다시 풀 수 있음 + 단어장이 모의에 맞춰지면 모의 점수가 부풀려져 판단을 망침). 저장소는 공개.
2. 키·비밀 커밋 금지(Azure 키 `.azure_speech` 등). 사용자 이메일 등 개인 정보도 저장소에 쓰지 않음.
3. **이미 있는 단어·장의 순서·id를 바꾸지 않음.** 새 단어는 뒤에만 붙임(append-only). 장 진도 키가 장 내용으로 정해져서, 앞을 건드리면 사용자 진도가 사라짐(5절).
4. 시험을 전부 통과한 빌드만 배포. 배포 뒤 라이브 확인(9절).
5. 목소리는 나나미(ja-JP-NanamiNeural)·게이타(ja-JP-KeitaNeural)만. 구글·애플 음성 금지.
6. 읽기는 히라가나. 한글 음차 금지. 카드 설명에 가타카나 읽기 금지.
7. 화면은 가볍게: 효과·애니메이션 추가 금지. 버튼 자리 바꾸지 않음.
8. `src/kanji_mn/kanji_src.json` 순서 고정(한자 단원 진도 키).
9. 예측·추정은 엄격한 가정으로만(사용자 요청). 낙관적인 숫자 금지.
10. 사용자에게는 한국어 해요체, 짧고 직접적으로. 긴 영어 문장 금지.
11. 서브에이전트(카드 작성·검수)는 저장소 폴더 `/home/claude/bjt-words`를 직접 건드리지 않음 — 자기 작업 폴더에 결과 파일만 쓰고, 합치기·커밋은 메인 세션이.
12. 사용자가 '취소', '하지 마'라고 하면 바로 멈추고 되돌림(11/9에 있었음).

## 3. 작업 환경 만들기 (세션마다 처음에)

스크립트에 경로 `/home/claude/work`, `/home/claude/bjt-words`가 박혀 있으니 그대로 써요.

```bash
# 저장소 (없으면). 예약 작업 등 새 세션에서 저장소가 안 붙어 있으면 add_repo(owner=qslns, repo=bjt-words, access=push) 먼저
[ -d /home/claude/bjt-words/.git ] || git clone https://github.com/qslns/bjt-words /home/claude/bjt-words
cd /home/claude/bjt-words && git fetch origin && git checkout expansion && git pull --rebase origin expansion
git config user.name qslns   # 커밋 작성자는 qslns (이메일은 저장소 기존 커밋과 같게: git log -1 --format=%ae main)

# 작업 폴더 = src/ 복사본 (이미 있으면 src가 더 새 것인지 보고 덮어씀)
mkdir -p /home/claude/work && cp -r /home/claude/bjt-words/src/. /home/claude/work/

# 파이썬 (분석·카드 검사)
pip install --break-system-packages -q fugashi unidic-lite edge-tts==7.3.1
# 음성 검사까지 할 때만 (용량 큼): torch는 CPU판
pip install --break-system-packages -q onnxruntime sherpa-onnx pyopenjtalk transformers
pip install --break-system-packages -q torch --index-url https://download.pytorch.org/whl/cpu

# 시험용 playwright: npm ci 하지 말 것(컨테이너에 깔린 브라우저와 버전이 어긋남) → 전역 것을 연결
mkdir -p /home/claude/work/app/node_modules && ln -sfn "$(npm root -g)/playwright" /home/claude/work/app/node_modules/playwright
```
- 시험 파일의 브라우저 경로는 11/13부터 `PW_CHROME` 환경 변수(없으면 기본 브라우저). 기본으로 안 뜨면 `PW_CHROME=$(ls -d /opt/pw-browsers/chromium-*/chrome-linux64/chrome | tail -1)`.
- 음성 검사 모델: `src/audioqa/README.md`. 받는 곳은 둘 다 `curl -L`로 받아짐(11/13 확인): HuggingFace `prj-beatrice/japanese-hubert-base-phoneme-ctc-v4`(→ `export_onnx.py`로 ONNX), GitHub 릴리스 `k2-fsa/sherpa-onnx` asr-models `sherpa-onnx-zipformer-ja-reazonspeech-2024-08-01.tar.bz2`. 모델 파일은 커밋 금지.

**기준선 확인(꼭)**: 아무것도 안 바꾼 상태에서
```bash
cd /home/claude/work && python3 app/make.py build/data_app.json app/test pwa https://qslns.github.io/bjt-words/ 120
python3 - <<'EOF'
import re; a=open('/home/claude/work/app/test/index.html',encoding='utf-8').read(); b=open('/home/claude/bjt-words/index.html',encoding='utf-8').read()
s=lambda x: re.sub(r"BUILD = '[^']*'", '', x); print('같음' if s(a)==s(b) else '다름 → 멈추고 원인부터')
EOF
```
11/13 확인: 같음. 다르면 src가 배포본과 어긋난 것이니 고치기 전에 원인을 찾아요.

**시험 서버**(컨테이너가 바뀌면 다시):
```bash
cd /home/claude/work/app/test && ln -sfn /home/claude/bjt-words/audio audio && ln -sfn /home/claude/bjt-words/icons icons && ln -sfn /home/claude/bjt-words/manifest.webmanifest manifest.webmanifest
(setsid nohup python3 -m http.server 8765 --bind 127.0.0.1 > /dev/null 2>&1 < /dev/null &)
cd /home/claude/work/app && bash run_revert_tests.sh && tail -2 t_revert_*.log && node kz_audio_test.mjs | tail -2 && node furi_test.mjs | tail -2
```
- **`app/test/audio` 연결이 없으면 음성 시험 7개가 실패**(11/13에 겪음: 217/7 → 연결 후 229/0).
- 11/13 기준 결과: 앱 시험 229/0 · 전체화면 9/0 · 업데이트 통과(나머지는 PROGRESS에 기록).

## 4. 동시 작업 잠금 (요약 — 자세한 건 PROGRESS.md 맨 위)

사용자와 대화하는 페이지와 예약 작업(3시간마다)이 같은 브랜치를 건드릴 수 있어요.
- 시작할 때 `git pull` → PROGRESS의 잠금이 남의 것이고 '마지막 신호'가 60분 안이면: **예약 작업은 아무것도 안 하고 끝냄**, 페이지(사용자와 대화 중)는 넘겨받음(잠금을 페이지로 바꿔 push).
- 일하는 동안 30분 안쪽마다 커밋·push하면서 '마지막 신호'를 고침. push 전에 `git pull --rebase` → 잠금이 남에게 넘어갔으면 지금 단위만 마무리해 push하고 멈춤.
- 끝낼 때: 한 일·다음 할 일 적고 잠금 '없음'으로 push.
- 사용 한도로 갑자기 끊길 수 있으니 **작은 단위(카드 100장, 패치 1개)로 자주 커밋**. 끊겨도 잃는 게 30분 안쪽이 되게.

## 5. 데이터 구조와 지켜야 할 것

`src/build/data_app.json` = `{words: [...], kanji: {...}, v: 3}`. make.py가 템플릿에 넣어 `index.html` 안 `<script type="application/json" id="bjt-data">`가 됨.

**단어** (본편 1,500 · 기본 885 · 둘 다 54 = 2,331개)
- 칸: `id w r m t c p y o hw ko kj kr e pr st` + 본편 `ord`(0부터) · 기본 `bn`(1부터) · 일부 `tw`(〜 들어간 표제어의 음성용 글).
- 예문 `e`: `{s, j, k, t, g}` — j는 `[漢字|よみ]` 루비 + `{표제어}`, t는 루비 뺀 글, g는 단어 풀이 `[[표제, 뜻], …]`.
- id: 본편 0~3815(띄엄띄엄), 기본만 있는 카드 9001~9885(= 9000 + bn, `src/basic/build_basic.py`의 BASE). 복원 카드는 옛 id(30~3830, 지금 id와 안 겹침 확인). **기본 추가는 9886부터(9000 + bn)**. 앱 코드에 id 자릿수 가정은 없었음(9000 검색 결과 없음) — 그래도 10000 넘는 id로 한 번 시험.
- 등급 t: 본편 S/A/B, 기본 K.

**장(章)과 진도** (`app2.tpl.html` 782~810줄)
- `genChapters`: 500개 묶음마다 250개 블록 안에서 50개씩 누적한 장 → 블록이 250 넘으면 묶음 총정리 → 전체가 500 넘으면 전체 총정리(all).
- 본편 장 키 = 500개 묶음 지문(그 묶음 id들의 해시) + 범위 + 종류. **1~1,500은 묶음 3개가 꽉 차 있어서 뒤에 붙여도 키가 안 바뀜** → 진도 유지. 바뀌는 건 '전체 총정리'(all) 하나뿐(내용이 1~3,812로 바뀌니 당연).
- **묶음을 덜 채워 배포하면 안 됨**: 1,501~1,750만 먼저 넣고 나중에 1,751~2,000을 채우면 4부 지문이 바뀌어 4부 진도가 전부 사라짐 → 복원은 **500개 단위로만 배포**(마지막 312개는 예외).
- 기본 장 키 = 장마다 그 장 id들의 해시 + 범위 + 종류. 기본 885 → 1,3xx로 늘리면 바뀌는 장: 751–885(→751–900), 501–885 총정리(→501–1,000), 기본 전체 총정리. 나머지 기본 장 진도는 그대로. → 배포할 때 사용자에게 이 세 장은 처음부터라고 알림.
- 단어 하나하나의 기록(H.w[id], 약점 등)은 id 기준이라 그대로.

**한자** `kanji[한자] = {h 훈음, b 부수, bn 부수 훈음, s 구성, x 풀이, on, kun, u 이 한자가 든 단어 id들, n 획수}`
- **u 순서(11/13 검증, 950자 전부 재현)**: 표제어 kj에 그 한자가 있는 단어 → 본편(ord 순) 먼저, 그다음 기본만 있는 카드(bn 순). 단어를 붙인 뒤 u를 이 규칙으로 다시 계산.
- 그림 카드(kz_cards)·한자 단원(kzo)은 kanji_src.json의 950자만. 그 밖 한자는 단어 카드에서 옛 방식(s·x)으로 그려짐(make.py 주석: "카드 없는 한자는 옛 자료로 그림").
- 새로 생기는 한자: 복원 표제어 408자(그중 407자는 10/4 옛 자료가 있음 → `old_kanji_extra.json`), 기본 추가 표제어 172자(옛 자료 61자, 나머지 약 111자는 새로 씀). 예문에만 나오는 한자는 항목이 없어도 됨.

**음성**
- 단어 `audio/w/<id>.mp3`(나나미), 예문 `audio/s/<id>-<번호>.mp3`(0·2번 나나미, 1번 게이타). 24kHz 48kbps 모노, 앞뒤 무음 자름(tools/regen_voice.py의 trim).
- 기기는 음성을 영구 저장(저장본 먼저) → **내용이 바뀐 파일은 주소에 ?v=해시가 붙어야** 새 소리를 받음. make.py가 `tools/voice_jobs.json`(기본 1,768) · `tools/audio_versioned.json` · audio/k · audio/kr 파일만 해시를 붙임.
  - 처음 생기는 파일(기본 추가 9886~): 해시 필요 없음.
  - 복원 카드의 옛 파일(audio/w·s에 아직 있음: w 4,662개 · s 9,656개 중 지금 카드 몫을 뺀 나머지)은 10/4 배포 때 기기에 저장됐을 수 있음 → **다시 만든 파일은 audio_versioned.json에 추가**.
- `tools/regen_voice.py`는 끝에 저장소 루트 `index.html`·`sw.js`를 직접 고침 → 확장 작업에서 쓰면 그 두 파일 변경은 되돌리고(`git checkout index.html sw.js`) make.py로 빌드. 새 음성은 따로 작업 목록 파일 + 같은 trim·edge 함수로 만드는 게 깔끔함.
- edge-tts가 막히면(10/10에 한 번, MS 토큰 변경) Azure 무료 키로 같은 목소리(`--engine az`) — 키는 사용자에게 받아야 함(저장소에 없음).

## 6. 단계별 방법

### P1 홈 정리
지금 홈(위에서부터): 설치 안내 · ★약점 단어 · 이어서/다음 순서 버튼 · [0부·기본 1 접기][0부·기본 2 접기] · **기본 전체 총정리 카드(접기 밖, 211px)** · [1부][2부][3부 접기] · **전체 총정리 카드(접기 밖)** · [한자 접기] · 전체 단어 목록·통계 · 사용법 · 저장 상태 · 버전. 확장하면 접기만 11개 + 큰 카드 2개.
바꿀 모양:
- 큰 접기 3개: **`0부 · 기본`**(기본 1–N) / **`BJT 단어`**(No.1–N) / **`한자`**(지금 그대로). 머리에 '끝낸 장 n/m' · '진행중'(지금 foldHTML과 같은 모양).
- 큰 접기 안: 500개 묶음마다 작은 접기(지금의 0부·기본 1, 1부·핵심 … 모양 그대로, 이름·범위·끝낸 장) + 맨 아래 총정리 카드(기본 전체 총정리 / 전체 총정리). 한자 접기는 이미 이 모양(kzHomeHTML 참고).
- 펼침 기억은 지금처럼 GOPEN(data-g 키: 'B','P','b0'…,'p0'…, 'kz'). 앱 쓰는 동안만 기억.
- 위 ★약점 · 이어서/다음 순서 버튼 · 아래 목록·통계는 그대로(사용자가 매일 누르는 곳).
- 머리 '단어 회독 N + 기본 M'은 자동으로 늘어남. 시험일이 지났으면(지금 기본값 10/22 → D+22) 'D+n' 대신 '시험일?'을 보여 주고 누르면 설정 › 시험일(작게, 선택).
- 방법: `app/patch_1113.py`(rep(옛 글, 새 글) 방식, patch_1021.py 참고) → `patch_app.py` 끝 exec 줄에 추가 → `python3 app/patch_app.py` → make.py.
- 시험: test_app.mjs는 홈 구조를 봄(`.grp-basic`, 묶음 수, openFolds가 `details.gf` 전부 펼침) → 새 구조에 맞게 고치되 **고친 기대값은 이유와 함께 PROGRESS에 적기**. 새 시험: 닫힌 홈 높이(세로 820×1180에서 한 화면 안쪽), 펼침·접힘 기억, 접기 안 장 카드 열기 → 단어 화면, 진도·이어서 하기 그대로, 콘솔 오류 0. 스크린샷(세로·가로)을 눈으로 확인.

### P2 기본 추가
1. 목록 확정: `basic_add.json`(471, 빈도 순) + `n3n2_missing.json` 앞쪽 기초 인사·정형 표현 → CARD_SPEC 5절 기준으로 빼고 더함 → `basic_final.json`(bn·id 붙여서, 순서 = 빈도 순). 뺀 것은 이유와 함께 PROGRESS에.
2. 작업 시트: 카드마다 표제·읽기·영어 뜻(JLPT 목록) + 같은 한자 단어(지금 덱) + gloss_dict 참고 → 서브에이전트에 100장씩.
3. 카드 작성(CARD_SPEC) → 검사기(아래 7절) 0 오류 → **다른 에이전트가 검수** TSV → 반영.
4. 새 한자 항목(약 111자): h(표준 훈음) b bn s x on kun n — 옛 자료 형식 그대로, 검사기로 훈음·읽기 확인.
5. 음성: 단어 + 예문(새 파일) → 받아쓰기 검사 → 틀린 것 다시.
6. 합치기: data_app.json 뒤에 붙임(bn 886~), kanji 추가 + u 다시 계산 → 빌드 → 시험 + 진도 보존 시험 → 배포.

### P3 복원 (2,312)
- 순서: `restore_order.json`(값 순서: 단어장 제작에 안 쓴 글 3종 — 비즈니스 대화 BSD · 유가증권보고서 chABSA · 문법·경어 드릴 문장 — 에서의 빈도. 근거 있는 말 1,676개가 앞, 근거 0인 636개는 옛 등급 → JLPT 급수 → id 순). 본편 ord 1500~3811.
- 500개씩(4부 1,501~2,000 → 5부 → … → 8부 3,501~3,812):
  1. 옛 카드(`old_words_2312.json`)를 CARD_SPEC 6절대로 손봄 — 특히 예문 풀이 `g`(옛 카드엔 없음), 10/7 이후 정한 읽기 규칙, 비슷한 예문.
  2. 검사기 → 다른 에이전트 검수 → 반영.
  3. 음성: 옛 파일을 받아쓰기 검사 → 틀린 것·글이 바뀐 예문만 다시 만들고 audio_versioned.json에 추가.
  4. 한자: `old_kanji_extra.json`에서 이 묶음 표제어에 필요한 항목 추가(옛 u는 버리고 다시 계산), 훈음이 지금 950자 쪽 표기 규칙과 맞는지 확인.
  5. 합치기(ord 이어서) → 빌드·시험·진도 보존 → 배포. 머리 이름: 4부~ '보충'(지금 lab 배열) 그대로 두거나 사용자에게 물어봄.

### P4·P5
- P4: 사용자 확인 전에는 `n3n2_missing.json`을 앱에 넣지 않음. 시간이 남으면 카드 초안만 `src/expansion/drafts/`에.
- P5: 묻기 전엔 안 함.

## 7. 카드 만들기 공정 — 10월 도구가 일부 없어요

**사라진 것(11/13 확인)**: 10월 작업 폴더의 `pipeline/build.py`(루비·TTS 글 만들기), `gloss/build_gloss2.py`(예문 풀이 g + 문맥 규칙 1,166건), `final/`(kanji_check·gloss_fix), `kanji/pick_readings2.py`, `gen_audio.py`, `corpus.py`, `basic/list.json`, `build/data_final.json`·`data1500g.json`. src 백업은 '빌드가 읽는 파일'만 챙겨서 이것들이 빠짐. → `src/basic/*.py` 대부분은 그대로는 안 돌아감(구조 참고용).
→ 새 방식: **작성자가 최종 꼴(루비 j, g, kr, ko)까지 직접 쓰고, 검사기가 엄격하게 확인.** 검사기는 새로 만들어요(`src/expansion/tools/check_cards.py` 권장):
- JSON 칸·형식, `{}` 정확히 1개, 루비 뺀 글 == 문장, 표제어 한자가 `{}` 안에 순서대로.
- 루비 읽기 vs fugashi(unidic) 읽기 비교 → 다르면 목록으로(사람·에이전트가 판정. 方·何·日 등은 문맥).
- kr 이어 붙인 것 == 표제 읽기의 한자 부분, 한자마다 읽기가 그 한자의 음·훈(kanji dict on/kun, 연탁·촉음 변형 허용)에 있는지.
- ko 음절 수 == 표제어 한자 수, 각 음절이 그 한자 훈음 h의 음과 같은지(두음법칙 허용).
- g: 예문 속 내용어(fugashi)가 풀이에 있는지(CARD_SPEC 4절 빼는 목록 제외), gloss_dict와 뜻이 다르면 경고.
- 예문 길이 12~45자, 숫자 뒤 조수사 루비 없음, 같은 덱 안 거의 같은 문장(문자 바이그램 유사도) 경고.
- 그다음 hw·kj·t를 만들고 data_app.json에 붙이는 합치기 도구(`append_cards.py` 권장): ord/bn 부여, pr 표제어 → id, kanji 추가, u 다시 계산(5절 규칙), 기존 단어는 바이트까지 그대로인지 확인.
  - hw 규칙(11/13 검증, 지금 카드 2,289/2,331 재현): 표제어의 한자 덩어리마다 `[덩어리|kr 읽기 이어 붙인 것]`, 가나는 그대로(`[手続|てつづ]き`, `[最寄|もよ]り[駅|えき]`). 나머지 42개 = kr이 빈 熟字訓(덩어리 전체에 r의 해당 부분: `[為替|かわせ]`)과 `〜` 표제어(루비 없이 w 그대로). 합치기 도구는 먼저 지금 2,331개에서 hw를 100% 재현하는지 시험하고 나서 새 카드에 씀.

서브에이전트: 사용자가 11/13에 "max 요금제를 다 써 버릴 생각이니 최대한 빡세게"라고 함 → 카드 작성·검수를 서브에이전트로 나눠 돌려도 됨. 단 작성자와 검수자는 다른 에이전트, 에이전트는 자기 폴더에만 씀(규칙 11), 결과는 메인이 검사기로 확인 후 합침. 에이전트에게는 CARD_SPEC.md 전문 + 작업 시트 + gloss_dict.json을 줌.

## 8. 음성 공정
1. 작업 목록(`f`, `v`, `t`, 필요하면 `rate`) — 단어는 표제어(〜 표제어는 tw 글), 예문은 t. 읽기가 갈리는 표제어는 가나로 넣되 **は로 시작하는 말을 히라가나로 넣으면 조사 わ로 읽음 → 가타카나로**.
2. edge-tts(나나미·게이타) 생성 → trim.
3. 받아쓰기 검사(`src/audioqa/`): 짧은 소리는 'これは … です' 사이에 넣어서, 예문은 쉼에서 잘라서, 두 인식기(음소 + ReazonSpeech). 숫자·조수사는 직접 판정.
4. 틀린 것: 넣는 글을 바꾼 후보 여러 개(그냥·가타카나·「」·쉼표·속도·목소리) → 두 인식기 다 통과한 것.
5. 인식기 버릇으로 판정해 둔 것(그대로 둠)은 audioqa/README.md 끝.

## 9. 빌드·시험·배포

배포 조건(전부):
1. 3절 기준선 확인을 이번 세션에서 했음.
2. 새 빌드로 앱 시험·전체화면·업데이트·한자 소리·후리가나 시험 전부 통과(기대값을 바꿨으면 이유를 PROGRESS에). 예상되는 기대값 변화: 단어 수·장 수·홈 구조, 그리고 '모든 단어 카드 … 0 old'(한자 칸이 전부 그림 카드) — 새 한자(그림 카드 없음)가 생기면 old > 0이 정상.
3. **진도 보존 시험**(새로 만듦, `app/progress_keep.mjs` 권장): 같은 주소에서 ① 지금 배포본 index.html로 진도를 만든다(기본·본편 장 몇 개 끝냄, 진행 중인 장, 약점·★, 한자 단원 기록, 설정) → ② 새 빌드로 바꿔 다시 연다 → 바뀌지 않아야 할 장 진도·단어 기록·이어서 하기·설정이 그대로인지, 5절에서 바뀐다고 한 장만 바뀌는지 확인.
4. 새 카드 검사기 0 오류 + 검수 반영 + 새·바뀐 음성 받아쓰기 통과.
5. 새 카드 전부 열기(세로·가로, 오류·빈칸·넘침 0), 홈 스크린샷 눈으로.
6. index.html 크기 기록(지금 약 5.8MB; 3,800+1,300단어면 10MB 안팎 예상 — 15MB 넘으면 멈추고 생각).

배포:
```bash
cd /home/claude/work && python3 app/make.py build/data_app.json app/dist pwa https://qslns.github.io/bjt-words/ 120
cp app/dist/index.html app/dist/sw.js /home/claude/bjt-words/
# src 갱신: 작업 폴더에서 바꾼 원본을 src로 (node_modules·test·dist·로그·모델·임시 파일 제외)
rsync -a --exclude node_modules --exclude 'app/test' --exclude 'app/dist' --exclude '*.log' --exclude __pycache__ --exclude 'models' --exclude '.tmp' /home/claude/work/ /home/claude/bjt-words/src/
cd /home/claude/bjt-words && git status --short | head   # 큰 파일·모델·키가 섞였는지 확인
git add -A && git commit -m "…" && git push origin expansion
git push origin expansion:main    # main으로 배포(fast-forward). 안 되면 main을 expansion에 먼저 merge
```
확인: 1~2분 뒤 `curl -s https://qslns.github.io/bjt-words/sw.js | grep VERSION`이 새 값, 바꾼 음성 몇 개 md5가 같은지. 사용자는 아이패드 크롬·사파리에서 주소로 열어 씀(홈 화면 아이콘 아님) — 새 버전은 홈 화면에서 자동 적용.
되돌리기: `git revert`로 index.html·sw.js를 전 상태로 → 다시 push(sw VERSION이 바뀌어야 기기가 받음).

## 10. 사용자에게 물어볼 것 (사용자와 대화 중일 때만, 작업은 막지 않음)
- P4(N3·N2 약 1,300개)를 넣을지.
- 다음 BJT 날짜(앱 시험일 설정용).
- 복원 묶음 이름(4부~: '보충' 그대로 / 다른 이름).

## 11. 이 폴더(src/expansion) 파일
| 파일 | 내용 |
|---|---|
| HANDOFF.md | 이 문서 |
| PROGRESS.md | 잠금 · 할 일 체크리스트 · 작업 기록 |
| CARD_SPEC.md | 카드 쓰는 법(작성·검수) |
| LESSONS.md | 10월~11월 시행착오와 교훈, 연혁 |
| old_words_2312.json | 10/5에 지운 단어 2,312개(10/4 배포본 2c45d8eb~1의 index.html에서 꺼냄, 옛 점수칸 sc·mk·ord는 뺌) |
| old_kanji_extra.json | 같은 배포본의 한자 항목 중 지금 950자에 없는 407자 |
| restore_order.json | 복원 순서(값 높은 순) |
| basic_add.json | N5·N4 목록 중 앱(복원분 포함)에 없는 말 471개, 빈도 순 |
| n3n2_missing.json | N3·N2 목록 중 없는 말 1,317개(P4, 확인 전) |
| gloss_dict.json | 지금 카드 예문 풀이 사전(표제 → [뜻, 횟수]) |
| ../tools/analysis/ | 빈도 분석 스크립트(make_lists.py가 위 목록을 만듦). 입력 글(BSD·chABSA·드릴 문장·JLPT 목록)은 저장소에 없음 — 다시 받는 곳은 LESSONS.md |
