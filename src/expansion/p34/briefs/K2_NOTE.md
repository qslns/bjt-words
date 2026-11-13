# 한자 그림 카드 — 11/14 덧붙임 (KANJI_SPEC.md 다음에 읽기, 이게 우선)

You write kanji picture cards in exactly the format and quality of `/home/claude/work/kz/KANJI_SPEC.md` (read it fully; it is in Korean). The 950 cards already in the app follow it. These new kanji come from words added to the app this week (basic N5·N4 words, then JLPT N3·N2 words); they will sit at the front of the app's kanji unit, so the user meets them first. Ignore the old context lines in KANJI_SPEC about "BJT 430점, 시험 10/22, 단어장 1,500 + 기본 885" — the user is now studying basic + N3·N2 words for the JPT (Nov 22, Dec 20). Everything else in KANJI_SPEC holds.

## Paths (different from KANJI_SPEC)
- Write ONLY inside your own folder `/home/claude/agents/<you>/`. `/home/claude/work` and `/home/claude/bjt-words` are read-only (the preview tool only touches its own lock file). Never run git.
- Approved samples: `/home/claude/agents/common/kz_gold/gold_s_p0.png`, `gold_s_p1.png` (small sheets) — open both before starting. Full-size: `gold_p0.png` … `gold_p3.png`. Source: `/home/claude/work/kz/gold.json`.
- Your batch file: `/home/claude/agents/<you>/<you>.json` (array of cards, KANJI_SPEC format).
- Tools (run from `/home/claude/work/kz`):
  - `python3 kzc.py info <all your kanji>` — once at the start (app 훈음, readings, words that use the kanji, KanjiVG parts tree with paths/stroke numbers, reference etymology).
  - `python3 kzc.py hun 字…` — standard 훈음 of a part.
  - `python3 kzc.py validate /home/claude/agents/<you>/<you>.json` — errors must be 0; resolve or justify every 주의.
  - `python3 preview.py /home/claude/agents/<you>/<you>.json /home/claude/agents/<you>/pv/<you> --sheet` — ALWAYS give the output path inside your folder; then Read only the new `_p*.png` sheets that contain the cards you just wrote.
- Temporary scripts/files: only inside your folder.

## Notes for these kanji
- The app 훈음 (`info` shows it) is fixed: the p3 caption must end with "→ <앱 훈음>" exactly. A few 훈음 are the classical Korean ones that differ from the Japanese meaning; aim the hook at the meaning the app's words use, and connect in `bridge` if needed.
- Many are very basic kanji (山, 川, 田, 犬, 魚, 鳥 …): pictographs → a clear picture of the thing (KANJI_SPEC "그림 글자"), `tree: []` + `basic`.
- No katakana anywhere. Readings in hiragana only, and only readings the app lists for the kanji.
- Work 5 cards at a time: write → validate → preview sheet → look → fix.

## Final report (short)
Batch file path, card count, validate result, kanji that were hard (one line each with your choice), part names not in the name table and your source, anything you are unsure about.
