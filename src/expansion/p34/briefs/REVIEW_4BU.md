# 4부 검수 덧붙임 (11/13) — REVIEWER_BRIEF.md와 같이 읽기

Read `/home/claude/agents/common/REVIEWER_BRIEF.md` fully first. These notes are newer and win where they differ.

## What these cards are
- Restore cards (`/home/claude/agents/p4rNN/out.jsonl`): old cards written 10/4, removed 10/5, re-edited today by another agent to the current standard. The old version of each card is in the same folder: `old_cards.json`. The editor's sheet with the kanji 훈음 (`kanji[].h`) is `sheet.json` there (per card: `no`, `old_card`, `kanji`, `homophones`).
- New N3·N2 cards (`/home/claude/agents/p4n/out.jsonl`, ids 20001+, `t` = "B"): written today; sheet `/home/claude/agents/p4n/sheet.json`.

## Audio cost — important
A restore sentence whose plain text (ruby and braces removed) is the same as in `old_cards.json` keeps its old audio. So do NOT propose a new sentence for taste. Propose a replacement (`jN` + `kN` + `gN` lines, and `sN` if the scene changes) only for a real error: wrong or unnatural Japanese, a use that does not show the headword's meaning, wrong politeness for the scene, a sentence that is (nearly) the same as another card in the app or in the other 4부 files, or material that looks taken from an official BJT mock/sample test. Ruby, gloss, translation, `m p y st ko kr pr` fixes are free.

## Check especially
1. Official BJT mock/sample material: question phrasing (「…はどれですか」「どの…ですか」 as a test question), passages/tables, or `p`/`st` text that refers to official samples, mock tests or specific test items (공식 샘플·모의·문항·청독해 표). Report with a replacement.
2. Near-duplicates across the whole 4부 set: compare sentences with the other files `/home/claude/agents/p4r*/out.jsonl`, `/home/claude/agents/p4n/out.jsonl` and the app deck `/home/claude/work/build/data_app.json`. The checker (`python3 /home/claude/work/expansion/tools/check_cards.py FILE --others '/home/claude/agents/p*/part_*.jsonl'`) flags ≥0.6; also report clearly-same sentences below that.
3. Glosses `g`: complete, correct for the context, dictionary form, same spelling as gloss_dict.
4. Readings in ruby (context readings, 連濁, counters after digits without ruby), `ko`, `st` 훈음 = sheet `h`.
5. `w`: if a headword is clearly better as an affix card (e.g. it is only ever used as `〜X`), report it in field `w` with the suggestion; the main session decides.

## Output
Your folder (given in the task): `review.tsv` as REVIEWER_BRIEF says (`id field current suggested reason`, last line `#SUMMARY 본 카드 n · 오류 n`) and `verdicts.md` with one line per "doubt" listed in your task (your decision + reason). Final message: the summary line and the 5 most important problems.
