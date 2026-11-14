# 한자 그림 카드 검수 — 11/14 덧붙임 (REVIEW_SPEC.md 다음에 읽기, 이게 우선)

You review new kanji picture cards that other agents wrote today, with the checklist of `/home/claude/work/kz/REVIEW_SPEC.md` (read it fully; Korean). Also read `/home/claude/work/kz/KANJI_SPEC.md` (the rules the writers followed) and `/home/claude/agents/common/K2_NOTE.md` (what the writers were told). The quality bar is the 950 cards already in the app: "검수는 필수, 배포 뒤 문제 있는 상황 절대 안 됨". Do not change good cards for taste.

## Paths (different from REVIEW_SPEC)
- The writers' files `/home/claude/agents/k2a0N/k2a0N.json` are read-only for you. First copy each batch you review to your own folder: `cp /home/claude/agents/k2a0N/k2a0N.json /home/claude/agents/<you>/k2a0N.json`, and fix only your copy.
- Write ONLY inside `/home/claude/agents/<you>/`. `/home/claude/work` and `/home/claude/bjt-words` are read-only (the preview tool only touches its own lock file). Never run git. Temporary files: only inside your folder.
- `review/flags.txt` does not cover these kanji — skip that step.
- Approved samples: `/home/claude/agents/common/kz_gold/gold_s_p0.png`, `gold_s_p1.png`.
- Tools (run from `/home/claude/work/kz`):
  - `python3 kzc.py info <kanji…>` (app 훈음, readings, words, KanjiVG parts) · `python3 kzc.py hun 字…`
  - `python3 kzc.py validate /home/claude/agents/<you>/k2a0N.json` — 0 errors; resolve or explain every 주의
  - `python3 preview.py /home/claude/agents/<you>/k2a0N.json /home/claude/agents/<you>/pv/k2a0N --sheet` — then Read every `_p*.png` sheet (all cards), and after fixing, the sheets with the cards you changed.
- Log: `/home/claude/agents/<you>/log.md` (REVIEW_SPEC "기록" format; one `검수 완료: k2a0N` line after each batch).

## Extra points for these cards
- No katakana anywhere; readings in hiragana and only readings the app lists for the kanji (`info`). A word reading in `snd`/`bridge` (e.g. 田舎 いなか) is fine only if it is clearly marked as the word's reading.
- Emoji: Unicode ≤ 13.1 (KANJI_SPEC). Check that each p3 emoji really shows the scene on a sheet.
- Gentle scenes: no gore, no cruelty, no stereotypes.

## Final report (short)
Per batch: cards, fixed cards, validate result. The 3 biggest problem types, and anything you are unsure about. The main session will take your copies as the final cards.
