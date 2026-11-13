# N3·N2 칸 카드 — 덧붙임 (11/13, 다른 지시문보다 이게 우선)

The app is getting new sections "N3 단어" and "N2 단어": JLPT N3/N2 words (not in the basic N5·N4 deck), ordered by importance, for the learner's JPT (Nov 22 / Dec 20), JLPT N2 (Dec 6) and a school entrance exam. Your cards go there (later some may also appear in the BJT section). The sheet field `no` is now like `N3 No.123` (rank in that section) and `jn` is the same number.

1. Keep the existing card style and rules (CARD_SPEC, your brief). Sentences stay business-flavoured, but a word that is not business-related (nature, body, daily life, feelings) should get a natural everyday sentence (scene `talk`) rather than a forced office scene. Never force a word into an odd business context.
2. `p` is shown under the label "BJT 포인트": write how/where the word is used (business and everyday), set phrases in 「」, pair words, confusion warnings (use `homophones`). Do not mention exams, question types or test items.
3. Similarity check: run the checker with `--others '/home/claude/agents/*/part_*.jsonl'` (all current writers and the 4부 editors), not `p*`.
4. `ko`: single-kanji words keep the plain 음 (涼 량, 冷 랭); 두음법칙 only on the first syllable of 2+-kanji words.
5. Never copy or imitate official BJT/JPT/JLPT test material (questions, passages, tables). Your own sentences only.
