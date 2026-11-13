# N3·N2 칸 검수 덧붙임 (11/13) — REVIEWER_BRIEF.md 다음에 읽기, 이게 우선

Read `/home/claude/agents/common/REVIEWER_BRIEF.md` fully first, then `/home/claude/agents/common/LV_NOTE.md` (rules the editors followed). These notes are newer and win where they differ.

## What these cards are
- They go into the app's new "N3 단어" section (JLPT N3 words by importance, for the learner's JPT/JLPT exams); some may later also appear in the BJT section.
- Restore cards: old cards (10/4) re-edited today. The old version is in the editor's folder (`old_cards.json`) or, for the review folders `rvn3x*`, in your own folder (`old_cards.json`, `sheet.json` with kanji 훈음 `h`).
- New cards (ids 20001+): written today from a word sheet (`sheet.json` in the writer's folder).

## Audio cost — important
A restore sentence whose plain text (ruby and braces removed) is the same as in the old card keeps its old audio. Do NOT propose a new sentence for taste. Propose a replacement (`jN` + `kN` + `gN`, and `sN` if the scene changes) only for a real error: wrong/unnatural Japanese, a use that does not show the headword's meaning, wrong politeness for the scene, a sentence (nearly) the same as another card in the app or in the other agents' files, an everyday word forced into an odd business scene, or material that looks taken from an official test. Ruby, gloss, translation, `m p y st ko kr pr` fixes are free.

## Check especially
1. Near-duplicates: compare with the app deck `/home/claude/work/build/data_app.json` and all other files `/home/claude/agents/*/part_*.jsonl`. The checker (`python3 /home/claude/work/expansion/tools/check_cards.py FILE --others '/home/claude/agents/*/part_*.jsonl'`) flags ≥0.6; also report clearly-same sentences below that.
2. Glosses `g`: complete, correct for the context, dictionary form, gloss_dict spelling.
3. Ruby readings (context readings, 連濁, counters after digits without ruby), `ko`, `st` 훈음 = sheet `h`.
4. `p` must not mention exams, test sections or question types (청해·독해 문제 등) — rewrite into plain usage notes.
5. Headword form (`w`): if a headword is really used only as an affix (〜氏, 〜陣, 〜気味, 旧〜…) or is a non-常用 spelling that the deck writes in kana (CARD_SPEC §2), give the full change in review.tsv: `w` and every field that must follow (`r`, `kr`, `ko`, `m`, `st`, `p`, and any `jN` whose braces/ruby must change). The main session decides.

## Output
Your folder (given in the task): `review.tsv` as REVIEWER_BRIEF says (`id field current suggested reason`, tab-separated; for `kr`, `pr` and `gN` put JSON in `suggested`; last line `#SUMMARY 본 카드 n · 오류 n`) and `verdicts.md` (one line per doubt listed in your task: your decision + reason). Final message: the summary line and the 5 most important problems (one line each).
