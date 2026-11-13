#!/usr/bin/env python3
"""한자 칸 새 순서(11/14, K1): 그 한자가 처음 나오는 단어 칸 순(기본 N5·N4 → N3·N2 → BJT만), 같은 칸 안은 많이 쓰는 순(신문 빈도)
- 대상 = 지금 앱 한자 + N3·N2 앞 1,000(복원·새 카드)에 나올 한자 전부 → 앞으로 N3 2부·N2를 붙여도 순서·장 키가 안 바뀌게
- 아직 앱에 없는 한자 항목은 지금 데이터에 미리 넣음(lv/kanji_future.json → append_cards --kanji): lvk1 · p34 · 옛 항목(드문 읽기는 kanji_readings_filter로 거름)
- 빈도: kanji-data(davidluzgouveia) freq(신문 빈도 순위, 없으면 뒤) (/home/claude/kzdata/dl/kanji.json)
출력: /home/claude/work/kanji_mn/kzo_v2.json {order, groups:[[이름, 수]]} · lv/kanji_future_raw.json
usage: python3 kanji_order.py"""
import json, sys, os
E = '/home/claude/work/expansion'
sys.path.insert(0, E + '/tools')
from cardlib import kj_of
from kanji_ref import ref
D = json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8')); K = D['kanji']
KD = json.load(open('/home/claude/kzdata/dl/kanji.json', encoding='utf-8'))
L = json.load(open(E + '/lv/lv_order.json', encoding='utf-8'))
OLD = {w['id']: w for w in json.load(open(E + '/old_words_2312.json', encoding='utf-8'))}
SRC = [json.load(open(E + f, encoding='utf-8')) for f in ('/lv/kanji_lvk1.json', '/p34/kanji_new_p34.json', '/old_kanji_extra.json', '/p2/kanji_new_p2.json')]
FIX_H = {'唇': '입술 순'}   # lvk1은 KANJIDIC 한국 음(진)만 보고 '놀랄 진' — 일본어 唇은 입술(脣과 같은 글자로 씀)
uses = {}
for w in D['words']:
    for c in dict.fromkeys(w['kj']): uses[c] = uses.get(c, 0) + 1
fut = {}
for sec in ('n3', 'n2'):
    for x in L[sec][:1000]:
        w = OLD[x['id']]['w'] if x['kind'] == 'R' else (x['w'] if x['kind'] == 'N' else None)
        if not w: continue
        for c in dict.fromkeys(kj_of(w)):
            uses[c] = uses.get(c, 0) + (0 if c in K else 1)
            if c not in K: fut[c] = 1
raw = {}
for c in fut:
    e = next((dict(s[c]) for s in SRC if c in s), None)
    if e is None: sys.exit('항목 없음: ' + c)
    if c in FIX_H:
        e['h'] = FIX_H[c]
        e['s'] = e.get('s', '').replace('놀랄 진', '입술 순')
    if not e.get('n'): e['n'] = ref(c)['n']
    raw[c] = {k: e[k] for k in ('h', 'b', 'bn', 's', 'x', 'on', 'kun', 'n') if k in e}
json.dump(raw, open(E + '/lv/kanji_future_raw.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
allk = list(K) + [c for c in fut if c not in K]
# 급수 = 그 한자가 처음 나오는 단어 칸(기본 N5·N4 → N3 → N2 → BJT만) — 단어 칸과 같은 묶음(kanji-data jlpt_new는 第·結·案이 N1이라 안 씀)
SEC = {}
def mark(c, g): SEC[c] = min(SEC.get(c, 9), g)
for w in D['words']:
    g = 0 if w.get('bn') is not None else 1 if w.get('jl') == 3 else 2 if w.get('jl') == 2 else 3
    for c in w['kj']: mark(c, g)
for sec, g in (('n3', 1), ('n2', 2)):
    for x in L[sec][:1000]:
        w = OLD[x['id']]['w'] if x['kind'] == 'R' else (x['w'] if x['kind'] == 'N' else None)
        if w:
            for c in kj_of(w): mark(c, g)
# 단, 아주 흔한 한자가 기본 단어에 가나로만 나와 뒤로 밀리지 않게(私 → N2가 되는 것 등) kanji-data 급수(jlpt_new)가 더 앞이면 그쪽
JG = {5: 0, 4: 0, 3: 1, 2: 2, 1: 3}
# N3·N2는 한 묶음(JPT용 — 안에서는 빈도 순이라 第·結 같은 흔한 한자가 앞으로), BJT에만 나오는 업무 한자는 맨 뒤(2월 BJT용)
def grp(c): return min({0: 0, 1: 1, 2: 1, 3: 2}[min(SEC.get(c, 3), JG.get((KD.get(c) or {}).get('jlpt_new'), 3))], 2)
NAMES = ['기본(N5·N4)', 'N3·N2', 'BJT']
key = lambda c: (grp(c), (KD.get(c) or {}).get('freq') or 9999, -uses.get(c, 0), c)
order = sorted(allk, key=key)
groups = [[NAMES[g], sum(1 for c in order if grp(c) == g)] for g in range(3)]
json.dump({'order': order, 'groups': groups, 'note': '11/14 K1: 처음 나오는 단어 칸(기본 → N3·N2 → BJT만, kanji-data 급수가 더 앞이면 그쪽) → 신문 빈도(kanji-data freq) → 단어 수'}, open('/home/claude/work/kanji_mn/kzo_v2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('한자', len(order), '(지금', len(K), '+ 미리 넣을', len(raw), ')', groups)
print('앞 30:', ''.join(order[:30]))
for g in range(3):
    gs = [c for c in order if grp(c) == g]; print(NAMES[g], ''.join(gs[:20]), '…', ''.join(gs[-8:]))
