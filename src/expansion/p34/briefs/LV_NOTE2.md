# N3·N2 칸 — 1부 검수에서 나온 것 (11/13 밤, LV_NOTE 다음에 읽기 · 이게 가장 새것)

Reviewers of N3 part 1 found the same problem again and again: **a sentence that copies the frame of a sentence already in the app** (same situation and predicate, only the nouns swapped). The checker's 0.6 score misses most of these (they scored 0.4–0.59). Before you keep any sentence, search the app deck (`/home/claude/work/build/data_app.json`, `words[].e[].j`) and the other agents' `part_*.jsonl` for its predicate/frame (for example `grep -c 遅れそうです`, `が増えている`, `を中心に`), and if the app already has that situation, write a different one.

Frames the deck already has many of — do not use them again (also not with other nouns):
- 同社は、(来年/〜に) 新工場を建設する/建てる · 同社は、〜と共同で〜を開発した
- 〜では、人手不足が深刻になっている · 〜を導入する企業が増えている · 〜を取り入れる企業が増えている
- この商品は、20代の女性/若い世代を中心に人気 · 〜を受けて、株価が大きく下落した/下がった · 景気は〜回復に向かっている
- 政府は、中小企業への支援を強化する方針だ · 主要国の景気…
- 今月の終わり/末までに、報告書/企画書を提出してください · 料金プランは、〜からお選びいただけます
- 事故で道が渋滞していて、30分ほど遅れそうです · 来週、お客様が工場の見学にいらっしゃいます
- 2つのプロジェクトを並行して担当するのは大変です · 先日、新聞社から取材の依頼がありました · H社の社長は、会見で〜を発表した
- 来月から、私が関西地区を担当することになりました · 新しい部長は、〜だそうです · お客様一人一人に合わせたプランをご提案します
- 検査の結果、機械に異常はありませんでした · 取引先から、値下げを要求されました · 何か困ったことがあれば、いつでも言ってください
- 使った物は、元の場所に片付けてください · 新しいシステム(の導入)に〜を感じる社員もいます · 初めてのプレゼンで、とても〜
- 会社の前の桜が、もう咲いていますよ · 太陽光発電を〜

Prefer concrete, varied, everyday situations for non-business words (nature, body, home, feelings, hobbies, travel, weather, school, family), as LV_NOTE says. A news-style sentence is fine only when the word is really a news word, and then pick a topic the deck does not already have.

Other points from the reviews:
- `p` must never mention exams or question types (청해·독해·문제·정답·그래프 문제 …). Write plain usage notes.
- Glosses: split set phrases into their words as the app does (「お祈り申し上げます」 → 祈る + 申し上げる). The gloss must fit THIS sentence (骨が折れる → 힘이 들다, not 부러지다).
- Counters/dates after digits: `[第|だい]1[月曜日|げつようび]` is right (the checker may flag 月 as a counter — that one is a false alarm).
- New kanji: the sheet `h` for kanji new to the app is final enough to use verbatim in `st`.
