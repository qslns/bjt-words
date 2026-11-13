# 새 한자 항목 쓰기 (N3·N2 칸, 11/13)

You write kanji entries for a Korean learner's Japanese word app. 108 kanji are new to the app (they appear in new JLPT N3/N2 word cards). Input: `/home/claude/agents/lvk1/sheet.json` (per kanji: `c`, `h` (the Korean 훈음 — filled for 14 of them, empty for the rest), `kh` (Korean 음 readings from KANJIDIC2), `on`, `kun` (KANJIDIC2 readings, katakana on / hiragana kun with `.okurigana`), `n` (strokes), `rad` (KANJIDIC radical), `en` (English meanings), `words` (the app words that use it)). Radical forms and names already used in the app: `radicals.json`. Finished examples in the app's style: `examples.json`.

For each kanji write:
- `h`: the standard Korean 훈음 used in Korean school/dictionary convention (`훈 음`, e.g. `형벌 형`, `심할 극`, `임금 왕`). Keep the 14 given ones unchanged. The 음 MUST be one of `kh` (check it). Use the 훈 for the meaning used in the listed `words` when a kanji has several standard 훈음 (e.g. 劇 심할 극 is standard; if a different standard 훈 fits the app words much better, you may use it).
- `b`: the radical as it appears in this kanji, in the form the app already uses (氵 not 水, 艹, 辶, 阝, 亻, 忄, ⺼ for flesh/月, 扌, 刂 …). If the kanji itself is a radical, b is the kanji.
- `bn`: the radical's Korean name in the app's style (see `radicals.json`; e.g. 삼수변, 초두머리(풀), 책받침(가다), 사람인변, 심방변, 육달월, 재방변, 선칼도방). For radicals not listed, use the standard Korean name.
- `s`: structure — parts with a 1–3 word Korean gloss each, e.g. `月(몸) + 复(복, 소리)`, `扌(손) + 叟(수, 소리)`. Pictographs: one line describing the picture.
- `x`: one sentence: how the parts make a concrete scene → the meaning(s), then example words in parentheses (Japanese words, preferably the listed `words`), e.g. `손(扌)으로 더듬어 찾음 → 찾다(捜す·捜査)`. Use `→` once before the meaning.
- `on`, `kun`: only readings actually used in common modern Japanese (drop rare/obsolete KANJIDIC readings). on in katakana, kun in hiragana with okurigana in parentheses: `さが(す)`. Keep every reading used by the listed `words`.

Rules (from the user, important): the learner must SEE the meaning from the scene. Concrete, intuitive pictures; no abstract chains; no sound puns; no invented etymology — if the traditional explanation is uncertain, write `옛 풀이로는 …` or describe the shape as a memory picture. Korean text only (no Japanese readings written in Hangul, no katakana in Korean text). Nothing scary/gory beyond what the meaning needs (殺 = 죽이다 is fine stated plainly).

Output: `/home/claude/agents/lvk1/out.json` — `{ "刑": {"h": "형벌 형", "b": "刂", "bn": "선칼도방", "s": "…", "x": "…", "on": ["ケイ"], "kun": []}, … }` with all 108 kanji. Write only inside `/home/claude/agents/lvk1/`; everything else is read-only; never run git. Validate with python3 that the file parses, has 108 keys, every `h` 음 is in `kh`. Final message: counts + any kanji you were unsure about (one line each).
