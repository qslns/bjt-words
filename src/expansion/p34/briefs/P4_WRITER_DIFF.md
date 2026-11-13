# P4 N3·N2 새 본편 카드 — WRITER_BRIEF와 다른 점 (11/13)

Read `/home/claude/agents/common/WRITER_BRIEF.md` fully and follow it, with these differences:

1. These are NOT basic cards. They are new main-deck cards ("BJT 단어", No.1,501 onward): JLPT N3/N2 words the app lacks, mixed by frequency with restored old cards. `t` is always `"B"` (not `"K"`). The learner meets them after ~1,500 business words, so sentences may use normal business vocabulary (still natural and short).
2. Sheet fields: `id` (20001+), `ord`, `no` (its number in the app), `w`, `r`, `en`, `lv`, `note` (decisions already made — follow them), `kanji`, `homophones`. Ignore anything about `bn` or "0부 · 기본".
3. Checker command:
   `python3 /home/claude/work/expansion/tools/check_cards.py /home/claude/agents/<you>/part_*.jsonl --sheet /home/claude/agents/<you>/sheet.json --others '/home/claude/agents/p*/part_*.jsonl'`
   The app deck it reads now includes the 445 new basic cards; the other 4부 editors' parts are in `--others`.
4. Affix cards (`〜性`, `大〜`, `〜科` …): sentences use real business compounds; the braces hold the affix only, with its ruby inside: `[安全|あんぜん]{[性|せい]}`, `{[大|だい]}[企業|きぎょう]`. `m` like `~성`; `p` gives 2–4 common business compounds and, when the sheet note says so, the plain word (e.g. 性 = 성별) as a warning.
5. `pr`: only words in the app, the restore list (`/home/claude/work/expansion/old_words_2312.json`) or your sheet.
6. Never copy or imitate official BJT mock/sample test material (question phrasing like 「…はどれですか」, its tables or passages). Your own sentences only.
