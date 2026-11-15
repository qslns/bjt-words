# 한자 그림 카드 N3·N2 — 11/15 덧붙임 (KANJI_SPEC.md → K2_NOTE.md 다음에 읽기, 이게 가장 우선)

These 326 kanji come from the app's N3·N2 words (the 1,000 most important JLPT N3 words + 1,000 N2 words the user studies for the JPT). In the app's kanji unit they come right after the 748 basic kanji. Replace K2_NOTE's line "Many are very basic kanji (山, 川 …)" with this:

## What is different in this group
- Few pictographs; many 형성자 and abstract meanings (党 무리, 委 맡길, 審 살필, 極 다할, 範 법, 序 차례, 令 하여금 …). KANJI_SPEC hook rule 2 still holds: the scene's action or state IS the meaning. Aim at the meaning the app's words use (`info` 단어: line) and show it as one concrete action. If you truly cannot find a concrete scene for a kanji, say so in your report instead of writing an abstract hook.
- Kokuji with no Korean sound: 枠 훈음 is just "틀" → p3 caption ends "→ 틀", final tree res `n` = "틀", no `r`; snd = 훈독 only.
- Classical 훈음 that differ from the Japanese meaning (滝 비올 롱 = waterfall, 芝 지초 지 = lawn, 畑 화전 전 = field, 缶 두레박 관 = can …): the caption still ends "→ <앱 훈음>" exactly; aim the scene at the Japanese meaning and connect in `bridge`.

## Gentle scenes (the user sees these every day)
- Never show a person or animal hurt, killed, shot or dead; no blood; no weapon pointed at anyone. 殺: e.g. swatting a mosquito or a bug — do not mention 自殺 anywhere on the card. 銃·撃·攻·爆·兵·軍·刑·犯·奪·侵·脅·暴: sports, toys, a target, fireworks, a cartoon thief, a startled cat — meaning clear, tone light.
- 裸: no nude person (e.g. a fruit 果 whose clothes 衤 came off, bare feet).
- 婦·嫁: no gender stereotypes (woman = broom/housework). Keep the real parts (女 + 帚 …) but frame neutrally, meaning from the words (主婦·夫婦·婦人 / 嫁·花嫁).
- 葬·墓·吐·酔·惨·毒·鬼·醜·尻·臓·骨: soft, not disgusting or scary (鬼 = a cute 도깨비).

## Other
- Readings exactly as `info` lists them (음독/훈독). Readings in hiragana only, no katakana anywhere.
- Same part = same name as in the 1,108 cards already in the app (validate warns from radicals.json — follow it unless you have a reason, and give the reason in your report).
- Keep your batch file valid JSON after every 5 cards: if a usage limit cuts you off, the main session resumes you and reuses what is there.
- In the final report also list kanji where the scene follows the Japanese meaning rather than the app 훈음.
