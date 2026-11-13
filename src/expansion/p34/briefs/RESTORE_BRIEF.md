# 복원 카드 손보기 지시 (P3, 11/13)

You edit vocabulary cards for a Korean learner's BJT (Business Japanese Test) word app. These cards were written on 10/4, removed on 10/5 when the deck was cut to 1,500 words, and now come back as numbers 1,501+. Since 10/4 the app's cards got stricter rules and per-word glosses; the old cards never got them. Your job: bring each old card up to the current standard while keeping what is already good.

## Hard rules for files
- Write ONLY inside your own folder `/home/claude/agents/<you>/`. Everything under `/home/claude/work` and `/home/claude/bjt-words` is read-only. Never run git.
- Never copy or imitate sentences from test-prep books, especially official BJT mock tests. New sentences must be your own.

## Read first (fully)
1. `/home/claude/work/expansion/CARD_SPEC.md` — the card spec (Korean), especially §4 (examples, glosses `g`) and §6 (restoring old cards).
2. `/home/claude/agents/common/examples.jsonl` — finished cards of the current standard (format, density).
3. Your `sheet.json`: per card `no` (its number in the app), `old_card` (the old card, already in output format, with empty `g` lists), `kanji` (for each headword kanji: `h` = the standard Korean 훈음 you MUST use verbatim in `st`, readings, app words with that kanji), `homophones`.
4. Gloss dictionary `/home/claude/work/expansion/gloss_dict.json` (headword → [[meaning, count], …]). For every word you put in `g`, use the most common meaning from it unless the context clearly needs another; keep the dictionary's spelling.

## What to do per card
1. **Add `g` to every example** (the main work): every content word a N4-level learner may not know, dictionary form `[표제, 짧은 뜻]`, NOT the headword, numbers, proper nouns, counters after digits, or these never-glossed basics: する いる この なる ある こと おる ござる そう よう その 私 いい よる 知る くる いう うち もの いつ ところ それ これ ほう なに. Keigo auxiliaries with the app's labels: ["いただく","~해 주시다(겸양)"] (or "(させて~) 제가 ~하다(겸양)"), ["いたす","하다(겸양)"], ["くださる","주시다"].
2. **Fix rule problems** the checker reports: readings (明日=あす, 私=わたくし in business speech, ○○会社=がいしゃ, 方 かた/ほう, 何 なに/なん, 日本=にほん, 人 じん/にん/ひと, 行 い/おこな, 通り どおり after a noun…), counters right after Arabic digits WITHOUT ruby (`3階`, `1週間`, `3種類`), `ko` with 두음법칙 only on the first syllable of 2+-kanji words (single-kanji words keep the plain 음: 来 래, 量 량), `st` using exactly the `h` from the sheet for each kanji (`漢(훈 음)`), lengths (m ≤22, p ≤70, st ≤100).
3. **Replace a sentence only when needed**: an error you cannot fix by ruby/gloss, unnatural Japanese, a wrong translation, or the checker says it is too similar (≥0.6) to an app sentence or another new card. Every changed sentence needs new audio, so do NOT rewrite sentences that are fine. A replacement must show the same use of the headword in a different situation, 12–35 characters, business scene, `{}` around the headword with ruby inside.
4. **Check the content**: the meaning `m` (short Korean, `·` between meanings), `p` (BJT point: where/which form it appears in business Japanese, set phrases in 「」, pair words, confusion warnings — use `homophones` from the sheet), `y` (easy Japanese paraphrase or synonym, may be empty), `o` (katakana loanwords only: `english(뜻)`), `st` (scene that makes the meaning visible; no invented etymology — if unsure `옛 풀이로는`; no sound puns; no 「」 around Korean words; Korean only, never Japanese readings in Hangul, never katakana readings in Korean text). Fix real errors; don't polish style for its own sake.
5. Keep `id`, `w`, `t` (A/B) as they are. Keep `r` unless it is wrong (then explain in the report). `pr` = confusable pair words as headword strings (only words that exist in the app, the restore list or your sheet).

## Output
JSONL, one card per line, fields exactly: `id w r m t c ko kr p y o st e pr` (examples: `s j k g`). Write in parts of about 15 cards: `part_01.jsonl`, `part_02.jsonl`, … At the end concatenate into `out.jsonl` in sheet order.

## Checker (after every part, and on out.jsonl at the end)
```
python3 /home/claude/work/expansion/tools/check_cards.py /home/claude/agents/<you>/part_*.jsonl --others '/home/claude/agents/p*/part_*.jsonl'
```
Fix every `E`. For `W`: fix missing glosses, wrong context readings, 훈음 mismatches, similar sentences, too-long fields. Acceptable to leave: fugashi's own misreadings (曜日 as ようひ, 日本 にっぽん, rendaku it misses), context readings you verified. Final out.jsonl: 0 errors.

## Final report (your last message)
Number of cards; checker SUMMARY line for out.jsonl; list of sentences you replaced as `id eN: reason` (one line each); warnings you deliberately left (one line each, with reason); any card you think should not be in the app or has a wrong headword/reading (explain, do not delete).
