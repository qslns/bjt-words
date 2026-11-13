# 카드 검수 지시 (P2~, 11/13)

You review vocabulary cards written by another agent for a Korean learner's BJT (Business Japanese Test) word app. You did not write them. Find REAL errors only.

## Files
- Cards to review: the `out.jsonl` path given in your task (one card per line; fields `id w r m t c ko kr p y o st e pr`; examples `s j k g`; `j` uses ruby `[漢字|よみ]` and `{}` around the headword).
- Spec: `/home/claude/work/expansion/CARD_SPEC.md` (read fully, especially §2–§4 and §7).
- Kanji 훈음 to check `st`/`ko`: the card writer's `sheet.json` in the same folder as out.jsonl (per card `kanji[].h`).
- Gloss dictionary for consistency of `g`: `/home/claude/work/expansion/gloss_dict.json`.
- You may run the checker for orientation: `python3 /home/claude/work/expansion/tools/check_cards.py <out.jsonl>` (it already passed with 0 errors; its warnings are hints, not verdicts).
- Write ONLY your review file into YOUR folder (given in the task). Everything else is read-only.

## What counts as an error (report these)
- Wrong or non-standard reading (`r`, `kr`, any ruby in `j`), including context readings: 方 かた/ほう, 何 なに/なん, 日本 にほん, 人 じん/にん/ひと, 行 い/おこな, 中, 後, 上, 間, 一日, 今日, 明日 must be あす, 私 in business speech わたくし, ○○会社 がいしゃ, 通り どおり after a noun, counters after digits must have NO ruby.
- Wrong or misleading meaning (`m`), wrong translation (`k`), mistranslated gloss (`g`), a missing gloss for a word a N4 learner would not know (except the never-glossed basics listed in CARD_SPEC §4), a gloss meaning that contradicts gloss_dict without reason.
- Unnatural or ungrammatical Japanese, wrong politeness for the scene, a sentence that does not show the headword's real use, two sentences of one card that are too similar.
- Wrong Korean hanja reading (`ko`: 두음법칙 only on the first syllable of words with 2+ kanji — 来月 내월; a single-kanji word keeps the plain 음 — 来 래, 緑 록), `st` 훈음 not equal to the sheet's `h`, invented or false etymology stated as fact, a sound-pun or abstract story (the user rejected those), wrong statements in `p`.
- Hangul transcription of Japanese (음차) anywhere, katakana readings written in Korean explanations, 「」 around Korean words in `st`.
- Gender-stereotyped scenes; anything copied from test-prep books.
Do NOT report matters of taste or style, alternative phrasings that are equally fine, or length unless over the limits (m ≤22, p ≤70, st ≤100 chars; sentences 12–35, max 45).

## Output
`review.tsv` in your folder, UTF-8, tab-separated, header line `id	field	current	suggested	reason`. `field` is one of `r m p y o ko st kr c pr` or per example `j0 j1 j2 k0 k1 k2 g0 g1 g2 s0 s1 s2`. `current` = the exact current value (for long fields, the part that is wrong), `suggested` = the full corrected value for that field (for `j`: the whole corrected `j` string with ruby and braces; for `g`: the whole corrected list as JSON), `reason` in short Korean. One line per problem. Last line: `#SUMMARY 본 카드 n · 오류 n`.
Final message: the summary line and the 5 most important problems (one line each).
