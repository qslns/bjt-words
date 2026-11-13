# 기본 추가 카드 작성 지시 (P2-3)

당신은 한국어 모국어 학습자용 BJT(비즈니스 일본어) 단어장 앱의 '0부·기본' 카드를 쓰는 작성자예요.

## 읽을 것 (먼저 끝까지)
1. 사양: `/home/claude/work/expansion/CARD_SPEC.md` — 칸 규칙·이야기·예문·풀이 전부 여기 따름.
2. 작업 시트: `/home/claude/agents/<내 폴더>/sheet.json` — 카드마다 id·bn·w·r·en(영어 뜻)·lv·note(정해 둔 표기 이유/메모 — 꼭 반영)·kanji(한자별 훈음 h·음·훈·같은 한자 덱 단어)·homophones(같은 소리 다른 말 → `p`에 헷갈림 주의 후보).
3. 지금 카드 예시: `/home/claude/work/build/data_app.json` 의 words 중 `bn`이 있는 카드(기본). 비슷한 품사 카드를 열어 보고 문체·길이·풀이 수준을 똑같이 맞춤. 예: python으로 `[w for w in words if w.get('bn')]`.
4. 풀이 사전: `/home/claude/work/expansion/gloss_dict.json` (표제 → [뜻, 횟수]). 예문 풀이 g는 여기 뜻을 먼저 씀.

## 할 일
- 시트의 카드마다 CARD_SPEC 1절 꼴 JSON 한 줄 → `/home/claude/agents/<내 폴더>/out.jsonl` (시트 순서대로, 한 줄에 하나, UTF-8).
- 칸: `id w r m t c ko kr p y o st e pr`. `id`·`w`·`r`은 시트 그대로(바꾸지 말 것). `t`는 `"K"`. `hw kj t(예문) bn ord`는 쓰지 않음(도구가 만듦).
- `pr`: 헷갈리는 짝이 있을 때만, 표제어 글자로(예 `["退院"]`). 없으면 `[]`.
- 예문 2개(뜻이 확실히 다른 중요 용법이 있으면 3개). BJT 장면(사내 대화·전화·방문·회의·메일·공지). 아주 기초어(この・はい・何 등)도 업무 장면에서 자연스럽게.
- 예문은 전부 직접 지음. 시험 문제집 문장을 옮기거나 흉내 내지 않음. 같은 카드 두 예문은 꼴·뜻이 달라야 하고, 지금 덱(4,994문장)의 문장과 거의 같으면 안 됨.
- 성별 고정관념 장면 금지(여직원=차 심부름 등). 실명 회사·인물 금지(가상의 이름 田中・山田 등은 괜찮음).
- 루비: 숫자 뒤 조수사 루비 없음, 明日=あす, 업무 문장의 私=わたくし, ○○会社=がいしゃ, 方·何·中·後·日·人 문맥 확인.
- 한국어에 「」 따옴표는 쓰지 않음(일본어 인용에만). 읽기는 히라가나, 한글 음차 금지.
- st 훈음은 시트 kanji[].h 그대로. 지어낸 어원 금지.

## 검사 (넘기기 전에 꼭)
```
python3 /home/claude/work/expansion/tools/check_cards.py /home/claude/agents/<내 폴더>/out.jsonl --sheet /home/claude/agents/<내 폴더>/sheet.json --others '/home/claude/agents/p2w*/out.jsonl'
```
- 오류(E) 0이 될 때까지 고침. 경고(W)는 하나씩 보고 맞으면 그대로, 틀리면 고침. 경고를 그대로 둔 것 중 판단이 필요한 건 `/home/claude/agents/<내 폴더>/notes.md`에 `id 경고 → 판단 이유` 한 줄씩.
- 결과 마지막 `#SUMMARY` 줄을 마지막 보고에 붙임.

## 규칙
- **자기 폴더(`/home/claude/agents/<내 폴더>/`)에만 씀.** `/home/claude/bjt-words`, `/home/claude/work`는 읽기만. git 명령 금지.
- 10장 정도마다 out.jsonl에 덧붙여 저장(끊겨도 남게). 처음부터 다시 쓰지 말고 이어서.
- 마지막 보고는 짧게: 쓴 장 수, #SUMMARY 줄, 판단이 애매했던 것 3개 이내.
