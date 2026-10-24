# 음성 오독 점검 (店 우선 + 남은 위험 읽기)

사용자 제보(10/15): "店의 텐도 무슨 '세니'… 이상하게 말함". 사용자는 음성 오독이 아직 남아 있다고 본다. 우리는 귀로 못 들으니, 예전처럼 **실제 앱 음성과 후보 읽기 합성음을 음향 비교**해서 찾는다.

## 자료
- 앱 음성: `/home/claude/bjt-words/audio/w/<단어id>.mp3`(단어), `/home/claude/bjt-words/audio/s/<단어id>-<예문번호>.mp3`(예문). 단어·예문 원문(후리가나 `[漢字|かな]`, 표제어 `{…}`): `/home/claude/work/build/data_app.json`의 `words[].e`.
- 목소리: 단어·예문 0/2번 = 나나미(ja-JP-NanamiNeural), 예문 1번 = 게이타(ja-JP-KeitaNeural). 합성 도구: 저장소 `tools/regen_voice.py`(edge-tts, `--engine edge`), 작업 목록 형식은 `tools/voice_jobs.json`, 지난 수정 기록 `tools/voice_fix.json`.
- 지난번 검증 스크립트(그대로 쓰거나 고쳐 쓰기): `/tmp/claude-0/-home-claude-bjt-words/4ecb1043-4c6e-5d36-a7b6-577be7533edc/scratchpad/sa2/`(verify_real.py, verify_cm.py, word_check.py, synth_*.py), `.../scratchpad/fin/mfcc_loc_lib.py`, `.../scratchpad/sa/sent_audit.py`. 방법: 후보 읽기마다 같은 목소리로 합성 → 앱 음성과 전체 정렬(DTW) → 그 낱말 구간만 MFCC 거리 비교 → 가장 가까운 후보가 바른 읽기가 아니면 오독. 대조군(확실히 바른 것)으로 판정이 맞는지 먼저 확인할 것.

## 할 일
1. **店이 든 모든 음성**(예문 107개 + 단어 店·店舗·支店·来店·開店·閉店·他店·入店·店員·喫茶店 등): 店 부분이 문맥상 바른 읽기(てん / みせ)로 났는지, 앞뒤 낱말(当店·代理店·2号店·全店·出店 등)까지 바르게 났는지. "세니"처럼 들린다는 제보 → 예를 들어 '店に'를 みせに로 읽어야 할 곳/てん이어야 할 곳이 바뀌었는지, 또는 다른 낱말이 깨졌는지.
2. 시간이 되면 같은 방법으로 **읽기가 갈리는 다른 한자 낱말**(지난번 점검 목록 `verify_all.json`/`verify_real.json`에 없던 것) 위주로 넓혀 본다. 숫자+조수사(3店舗, 5店舗 등)도 확인.
3. 오독 의심마다: 단어id-예문번호, 원문, 기대 읽기, 들린 것으로 보이는 후보, 점수 차이(근거)를 표로.
4. 고칠 것: 그 낱말만 히라가나로 바꾼 TTS 입력으로 **같은 목소리로 다시 합성**해 `/tmp/claude-0/-home-claude-bjt-words/4ecb1043-4c6e-5d36-a7b6-577be7533edc/scratchpad/audiofix/<id>-<n>.mp3`에만 저장하고, 새 파일이 바른 읽기로 판정되는지 같은 방법으로 확인. **저장소(/home/claude/bjt-words)는 절대 건드리지 말 것** — 배포는 내가 한다. 바꾼 TTS 입력 목록은 `.../scratchpad/audiofix/fixes.json`(지난번 voice_fix.json 형식)으로.

## 주의
- CPU가 2개뿐이고 다른 작업도 돈다. 큰 일괄 처리는 나눠서, 오래 걸리는 건 진행 상황을 파일로 남기며.
- 합성(edge-tts)이 막히면 그 사실을 보고하고 분석만.
- 임시 파일은 `.../scratchpad/audiofix/` 안에만.

## 마무리 보고
점검한 개수, 오독으로 판정된 것 목록(근거 포함), 다시 만든 파일 목록과 재검증 결과, 확신 못 하는 것.
