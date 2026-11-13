# 카드 작성 지시 (P2 기본 추가, 11/13)

You write vocabulary cards for a Korean learner's BJT (Business Japanese Test) word app. The learner is Korean, knows about half of JLPT N5–N4, studies by fast repeated passes, reads Japanese readings only in hiragana. These cards are the app's "0부 · 기본" (basic N5–N4 words), but every example sentence is set in a business scene.

## Hard rules for files
- Write ONLY inside your own folder `/home/claude/agents/<you>/`. Everything under `/home/claude/work` and `/home/claude/bjt-words` is read-only for you. Never run git.
- Never copy or imitate sentences from test-prep books, especially official BJT mock tests. Write every sentence yourself.

## Read first (fully)
1. `/home/claude/work/expansion/CARD_SPEC.md` — the card spec (Korean). It is the authority.
2. `/home/claude/agents/common/examples.jsonl` — 15 finished cards from the app in exactly the output format. Match their style, density and length.
3. Your sheet `sheet.json` in your folder. Per card: `id`, `bn`, `w` (headword — keep exactly), `r` (reading), `en` (JLPT English meaning), `lv`, `note` (decisions already made — follow them), `kanji` (for each kanji in the headword: `h` = the standard Korean 훈음 you MUST use verbatim in `st`, plus on/kun readings and `deck_words` = app words with that kanji), `homophones` (app words with the same reading — warn in `p` when confusable).
4. Gloss dictionary `/home/claude/work/expansion/gloss_dict.json` (headword → [[meaning, count], …], most used first). For every word you put in `g`, look it up (e.g. `python3 -c` or grep) and reuse the most common meaning unless the context clearly needs another. Keep the same headword spelling as the dictionary (it links to other cards).

## Output
JSONL, one card per line, fields exactly: `id w r m t c ko kr p y o st e pr` (CARD_SPEC §1). `t` is always `"K"`. `id`, `w` from the sheet; keep `r` from the sheet unless it is wrong (then explain in your final report).
Write in parts of about 15 cards: `part_01.jsonl`, `part_02.jsonl`, … (each a complete JSONL file). At the end concatenate them into `out.jsonl`.

## Checker (run after every part, and on out.jsonl at the end)
```
python3 /home/claude/work/expansion/tools/check_cards.py /home/claude/agents/<you>/part_*.jsonl --sheet /home/claude/agents/<you>/sheet.json --others '/home/claude/agents/p2w*/part_*.jsonl'
```
Fix every `E` (error). For `W` (warning) fix real problems: missing `g` glosses, a ruby reading that is wrong in this context, `ko`/`st` 훈음 mismatch, sentences too similar to another card, too long fields. Some warnings are expected and fine to leave: fugashi's own misreadings (e.g. 曜日 as ようひ, にっぽん for 日本, 一日=ついたち when the date is meant), context readings you verified (方 かた/ほう, 何 なに/なん, 人 じん/にん). The final out.jsonl must have 0 errors.

## The rules people break most (all from CARD_SPEC)
- Sentences: natural, short business Japanese, 12–35 characters (max 45). Conversation in です・ます, notices/documents in written style. Two sentences per card showing clearly different uses or situations (3 only if a clearly different important use exists). No near-duplicates of each other or of other cards (the checker compares). Scenes `s`: tel mtg talk visit biz graph doc mail notice report news. Vary people and roles; no gender stereotypes.
- Ruby `j`: every kanji run as `[漢字|よみ]` in hiragana, okurigana outside (`お[送|おく]りします`). The headword exactly once inside `{}`, conjugated if natural, with its ruby inside: `{[入院|にゅういん]}`, `{[確認|かくにん]し}`. Numbers are Arabic digits (3月10日, 20%, 5,000円) and a counter right after a digit has NO ruby (`3階`, `1週間`, `500円`, `3{軒}`). Removing the ruby and braces must give the plain sentence.
- Context readings: 明日=あす, 私=わたくし in business speech, ○○会社=がいしゃ (親会社), 方 かた(person)/ほう(side), 何 なに/なん, 日本=にほん, 人 じん/にん/ひと, 行 い/おこな, 通り どおり after a noun, 一日 いちにち/ついたち, 中 なか/ちゅう/じゅう, 後 あと/のち/ご, 間 あいだ/ま/かん.
- `g` (glosses): every content word in the sentence a N4-level learner may not know, in dictionary form `[표제, 짧은 뜻]` — but NOT the headword, numbers, proper nouns, counters after digits, or these never-glossed basics: する いる この なる ある こと おる ござる そう よう その 私 いい よる 知る くる いう うち もの いつ ところ それ これ ほう なに. Include keigo auxiliaries with the label used in the app: ["いただく","~해 주시다(겸양)"] (or "(させて~) 제가 ~하다(겸양)"), ["いたす","하다(겸양)"], ["くださる","주시다"].
- `ko`: Korean hanja reading of each headword kanji in order (the 음 = last syllable of `h`). 두음법칙 only on the first syllable of words with 2+ kanji (来月 내월, 料理 요리, 緑茶 녹차); a single-kanji word keeps the plain 음 like the app's cards (来 래, 量 량, 緑 록, 履く 리). Empty for kana-only words. `々` repeats the previous syllable.
- `kr`: the reading of each kanji in THIS word, hiragana, concatenated = the kanji part of `r` (rendaku/sokuon included: 日本 → [["日","に"],["本","ほん"]], 一緒 → いっ+しょ). For readings that cannot be split per kanji: a chunk (`[["小売","こうり"]]`) or, for 熟字訓, an empty list (二十歳, 今日 → []).
- `st` (Korean, ≤100 chars): kanji words `漢(훈 음)+字(훈 음): how the two meanings combine → the word's meaning.` using EXACTLY the `h` from the sheet. If Korean has the same word: `한국어 '○○'와 같은 말.` Single kanji: the picture/scene of the kanji → meaning. Kana words: the real kanji origin if there is one (`한자로 ○○(훈 음)`) or a vivid concrete hook. Katakana words: English origin + hook (and `o` = `english(뜻)`). No invented etymology or history (if unsure, say `옛 풀이로는`), no sound puns, no abstract chains — the learner wants to SEE the meaning. No 「」 around Korean words.
- `p` (Korean, ≤70 chars): BJT point — where and in which form it shows up in business Japanese (set phrases in 「」), its pair words, politeness level (e.g. じゃあ is casual, では formal), and confusion warnings (homophones from the sheet, similar words).
- `m`: short Korean meaning ≤22 chars, several meanings joined with `·`. `y`: easy Japanese paraphrase or synonym (may be empty). `o`: only for katakana loanwords.
- Never write Japanese readings in Hangul (no 음차) and never write katakana readings in Korean explanations — readings are hiragana.
- `c` category: org mtg sch tel doc deal money sales graph hr trouble verb formal kata keigo it gen (all katakana loanwords = kata).
- `pr`: confusable pair words as headword strings (only words that exist in the app or in your sheet), may be empty.

## Very basic words
Even この, それ, はい, 寝る, 犬 get two BJT-scene sentences (office, phone, meeting, notice, report…). Keep them natural; a dog can appear in a pet-food sales report, a cat in a customer call about a pet hotel, etc. Numerals 一~十 and 零: use natural compounds where the kanji numeral is standard (第三者, 四半期, 四捨五入, 二重, 十分, 一部, 九州, 零細企業, 七五三…), with `{}` around the numeral kanji only and ruby per kanji (`[第|だい]{[三|さん]}[者|しゃ]`). The braces content for counters/〜 headwords is the suffix itself (`[田中|たなか]{さん}`, `3{軒}`).

## Final report (your last message)
Number of cards, the checker SUMMARY line for out.jsonl, warnings you deliberately left (one line each with the reason), and any sheet decision you think is wrong (do not change `w`; explain).
