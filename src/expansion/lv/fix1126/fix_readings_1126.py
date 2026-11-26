#!/usr/bin/env python3
"""11/26 점검: 덱 단어 kr이 쓰는 常用 읽기인데 한자 카드 읽기 목록에 없던 것 더하기 + 贅 음 고치기
- 生 は(える)·は(やす)(生える·生やす)·き(生地) / 冷 さ(める)·さ(ます)(冷める·冷ます) / 素 もと(素) / 銭 ぜに(小銭) / 直 じか(直に) / 各 おのおの(各々)
- 贅: 옛 KANJIDIC(2010 전)의 セイ만 들어가 있었음 → 常用 읽기 ゼイ(贅沢 ぜいたく)로 바꿈(그림 카드는 아직 없음 — K2c 합칠 때 앱 자료에서 들어감)
고치는 곳: 앱 자료 kanji on/kun · 그림 카드 kz_cards on/kun · 읽기 중요도 kz_imp(흘려보기로 뒤에 덧붙임 — 대표 소리·순서는 그대로, 11/16 中 じゅう와 같은 방식)
usage: python3 fix_readings_1126.py DATA_IN DATA_OUT   (kz_cards.json·kz_imp.json은 제자리 고침, 처음 한 번 *_pre_1126.json 백업)"""
import json, sys, os, shutil
DI, DO = sys.argv[1:3]
KC, KI = '/home/claude/work/kz/kz_cards.json', '/home/claude/work/kz/kz_imp.json'
for p in (KC, KI):
    b = p.replace('.json', '_pre_1126.json')
    if not os.path.exists(b): shutil.copy(p, b)
ADD_KUN = {'生': ['は(える)', 'は(やす)', 'き'], '冷': ['さ(める)', 'さ(ます)'], '素': ['もと'], '銭': ['ぜに'], '直': ['じか'], '各': ['おのおの']}
D = json.load(open(DI, encoding='utf-8')); K = D['kanji']
C = json.load(open(KC.replace('.json', '_pre_1126.json'), encoding='utf-8'))
I = json.load(open(KI.replace('.json', '_pre_1126.json'), encoding='utf-8'))
CB = {c['c']: c for c in C}
for ch, adds in ADD_KUN.items():
    k = K[ch]; c = CB[ch]; x = I[ch]
    for r in adds:
        if r not in k['kun']: k['kun'] = k['kun'] + [r]
        if r not in c['kun']: c['kun'] = c['kun'] + [r]
        if not any(rr == r for rr, _, _ in x['kun']):
            x['kun'] = x['kun'] + [[r, max(n for _, n, _ in x['on'] + x['kun']) + 1, 1]]
    print(ch, 'app', k['on'], k['kun'], '| card', c['on'], c['kun'], '| imp', x['on'], x['kun'], x['rep'])
assert K['贅']['on'] == ['セイ'], K['贅']
K['贅']['on'] = ['ゼイ']
assert '贅' not in CB and '贅' not in I
print('贅', K['贅'])
json.dump(D, open(DO, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(C, open(KC, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(I, open(KI, 'w', encoding='utf-8'), ensure_ascii=False)
