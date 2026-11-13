#!/bin/bash
# P2 합치기 (11/13): 검수 반영 카드 → 음성 작업 목록(tt) → data_app.json 뒤에 붙임
# 전제: HANDOFF 3절 작업 폴더 /home/claude/work (build/data_app.json = 배포본 데이터)
set -e
T=/home/claude/work/expansion/tools; P=/home/claude/bjt-words/src/expansion/p2; A=/home/claude/aqa
mkdir -p $A
python3 $P/apply_review.py
python3 $T/audio_jobs.py $P/cards_final.jsonl --out $A/p2_jobs.json
python3 $T/append_cards.py --data /home/claude/work/build/data_app.json --out $A/data_p2.json --order /home/claude/work/expansion/basic_final.json \
  --cards $P/cards_final.jsonl --kanji $P/kanji_p2_all.json --tt $A/p2_jobs_tt.json
echo "→ $A/data_p2.json (확인 뒤 build/data_app.json으로 복사)"
