#!/usr/bin/env python3
"""N3 3부(11/16): 年中(ねんじゅう)이 처음으로 中=じゅう kr을 씀 → 中 한자 읽기에 ジュウ 더함(사전 デジタル大辞泉 中 ［音］チュウ・ジュウ: 一日中·世界中)
앱 한자 자료 on · 그림 카드 kz_cards on · 읽기 중요도 kz_imp on(③, 흘려보기 아님 — 대표 소리 ちゅう·なか 그대로)
usage: python3 fix_chuu.py DATA_IN DATA_OUT   (kz_cards.json·kz_imp.json은 제자리 고침, 처음 한 번 *_pre_n3p3.json 백업)"""
import json, sys, os, shutil
DI, DO = sys.argv[1:3]
KC, KI = '/home/claude/work/kz/kz_cards.json', '/home/claude/work/kz/kz_imp.json'
for p in (KC, KI):
    b = p.replace('.json', '_pre_n3p3.json')
    if not os.path.exists(b): shutil.copy(p, b)
D = json.load(open(DI, encoding='utf-8'))
k = D['kanji']['中']
if 'ジュウ' not in k['on']: k['on'] = k['on'] + ['ジュウ']
C = json.load(open(KC.replace('.json', '_pre_n3p3.json'), encoding='utf-8'))
for c in C:
    if c['c'] == '中' and 'じゅう' not in c['on']: c['on'] = c['on'] + ['じゅう']
I = json.load(open(KI.replace('.json', '_pre_n3p3.json'), encoding='utf-8'))
x = I['中']
if not any(r == 'じゅう' for r, _, _ in x['on']):
    x['on'] = x['on'] + [['じゅう', max(n for _, n, _ in x['on'] + x['kun']) + 1, 1]]   # 흘려보기(접미 〜中 じゅう) — 대표 소리 ちゅう·なか 그대로
json.dump(D, open(DO, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(C, open(KC, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(I, open(KI, 'w', encoding='utf-8'), ensure_ascii=False)
print('中', k['on'], [c['on'] for c in C if c['c'] == '中'], I['中']['on'])
