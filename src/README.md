# 단어장 앱 소스 백업 (src/)

https://qslns.github.io/bjt-words/ 를 만드는 원본이에요. 앱은 이 폴더를 읽지 않아요 — 실제로 쓰는 건 저장소 루트의 `index.html`·`sw.js`·`audio/` 뿐.

- 기준: 2026-10-25, 배포 커밋 9e7c8d6과 같은 상태.
- 이 소스로 다시 빌드하면 빌드 시각(`BUILD`)과 `sw.js`의 `VERSION` 말고는 배포 파일과 바이트 단위로 같아요(10/25 확인).

## 폴더

| 경로 | 내용 |
|---|---|
| `app/` | `app.tpl.html`(원본) → `patch_app.py`가 `patch_1015.py`~`patch_1021.py`를 차례로 적용해 `app2.tpl.html` 생성 → `make.py`가 데이터·음성 해시를 넣어 `index.html`·`sw.js` 생성. `*.mjs`는 테스트 |
| `build/data_app.json` | 단어·예문 데이터 |
| `kanji_mn/` | 한자 데이터. `kanji_src.json`은 **순서 고정**(바꾸면 진도가 꼬여요) |
| `kz/` | 한자 카드 `kz_cards.json`·`kz_imp.json`, 렌더러 `kz_render.js`·`kz.css`, 사양 `*_SPEC.md`, 제작 배치·검수 기록 |
| `basic/` | 기본 단어(N5·N4) 덱 제작 스크립트·작업 시트 |
| `audioqa/` | 음성 전수 검사 도구 (`audioqa/README.md`) |
| `../tools/` | 음성 만들기·버전 관리(`voice_jobs.json`, `kanji_voice.py`, `regen_voice.py`, `audio_versioned.json`) — 원래 저장소에 있던 것 |

빌드가 실제로 읽는 파일(10/25 추적): `app/` 템플릿·패치·`make.py`·`sw.tpl.js`, `build/data_app.json`, `kanji_mn/kanji_src.json`, `kz/kz_cards.json`·`kz_imp.json`·`kz_render.js`·`kz.css`, 저장소의 `audio/`·`tools/voice_jobs.json`·`tools/audio_versioned.json`.

## 복원

스크립트에 경로 `/home/claude/work`, `/home/claude/bjt-words`가 박혀 있어서 그 자리에 둬요.

```
git clone https://github.com/qslns/bjt-words /home/claude/bjt-words
mkdir -p /home/claude/work && cp -r /home/claude/bjt-words/src/. /home/claude/work/
cd /home/claude/work/app && npm ci          # 테스트용 playwright
```

## 빌드

```
cd /home/claude/work
python3 app/patch_app.py                     # 패치를 고쳤을 때만 (app2.tpl.html 다시 만듦)
python3 app/make.py build/data_app.json app/test pwa https://qslns.github.io/bjt-words/ 120   # 테스트용
python3 app/make.py build/data_app.json app/dist pwa https://qslns.github.io/bjt-words/ 120   # 배포용
```

인자: 데이터, 출력 폴더, 모드, 앱 주소, 음성 캐시 MB.

## 테스트

```
cd /home/claude/work/app/test && (setsid nohup python3 -m http.server 8765 --bind 127.0.0.1 > /dev/null 2>&1 < /dev/null &)
cd /home/claude/work/app && bash run_revert_tests.sh && tail -2 t_revert_*.log
node kz_audio_test.mjs && node furi_test.mjs
```

컨테이너가 다시 시작되면 테스트 서버가 꺼지니 다시 띄워요.

## 배포

1. `app/dist/index.html`·`sw.js`를 저장소 루트로 복사
2. 바뀐 파일만 `git add`(필요하면 `audio/`·`tools/`도) → 커밋(작성자 qslns) → push
3. 라이브 `sw.js`의 `VERSION`이 새 값인지, 바꾼 음성 파일 md5가 같은지 확인

테스트를 전부 통과한 빌드만 배포해요.

## 일부러 뺀 것

- 공식 모의 문제에서 뽑은 자료(빈도 집계 등). 저장소가 공개이고, 시험 전에 내용이 노출되면 안 돼서요. `basic/`의 후보 선정 단계(`cands*.json`·`list.json`·`select.py`·`merge.py`·`show.py`)도 이 때문에 뺐어요.
- Azure 키(`.azure_speech`) — 절대 커밋 금지.
- `node_modules`, 스크린샷 스크립트·이미지, 로그, `*.bak`, `kz/preview/`(미리보기 이미지 146MB).
- 음성 인식 모델 파일 — 받는 곳은 `audioqa/README.md`에 있어요.
