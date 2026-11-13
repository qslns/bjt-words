#!/usr/bin/env python3
"""기본 501~ 재배열(11/13): lv_order.json의 basic_tail 순서로 bn을 다시 매김. 1~500은 그대로.
바뀌는 것: 단어의 bn(501~) + 한자 u(단어 목록 순서). 다른 건 바이트까지 같아야 함.
usage: python3 reorder_basic.py DATA_IN LV_ORDER DATA_OUT → EXPECT_GONE 줄 출력"""
import sys, json
sys.path.insert(0, '/home/claude/work/expansion/tools')
from append_cards import compute_u, dump
din, lvp, dout = sys.argv[1:4]
D = json.load(open(din, encoding='utf-8')); L = json.load(open(lvp, encoding='utf-8'))
W = D['words']; byid = {w['id']: w for w in W}
B = sorted([w for w in W if w.get('bn') is not None], key=lambda w: w['bn'])
assert [w['bn'] for w in B] == list(range(1, len(B) + 1)), 'bn 빈틈'
tail = L['basic_tail']
assert sorted(x['id'] for x in tail) == sorted(w['id'] for w in B[500:]), '501~ 구성이 다름'
assert all(byid[x['id']]['bn'] == x['old_bn'] for x in tail), 'old_bn 안 맞음(데이터가 바뀜)'
before = {w['id']: dump(w) for w in W}; kb = {c: dump(k) for c, k in D['kanji'].items()}
for x in tail: byid[x['id']]['bn'] = x['new_bn']
B2 = sorted([w for w in W if w.get('bn') is not None], key=lambda w: w['bn'])
assert [w['bn'] for w in B2] == list(range(1, len(B2) + 1)) and [w['id'] for w in B2[:500]] == [w['id'] for w in B[:500]]
U = compute_u(W, D['kanji'])
for c, k in D['kanji'].items(): k['u'] = U[c]
for w in W:
    o = json.loads(before[w['id']]); o['bn'] = w.get('bn')
    if o.get('bn') is None: o.pop('bn', None)
    assert dump(o) == dump(w), ('단어가 bn 말고도 바뀜', w['id'])
nu = 0
for c, k in D['kanji'].items():
    o = json.loads(kb[c]); nu += o['u'] != k['u']; o['u'] = k['u']; assert dump(o) == dump(k), c
json.dump(D, open(dout, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('bn 바뀐 단어', sum(byid[x['id']]['bn'] != x['old_bn'] for x in tail), '/', len(tail), '· u 바뀐 한자', nu)
# 진도 키가 바뀌는 기본 장(genChapters 그대로)
def gen(total):
    out = []
    for p in range(0, (total + 499) // 500):
        ps = p * 500 + 1; pe = min(total, ps + 499); bs = ps
        while bs <= pe:
            be = min(pe, bs + 249); e = min(be, bs + 49)
            while True:
                out.append((bs, e, 'step'))
                if e >= be: break
                e = min(be, e + 50)
            bs += 250
        if pe - ps + 1 > 250: out.append((ps, pe, 'review'))
    if total > 500: out.append((1, total, 'all'))
    return out
gone = ['B:%d-%d:%s' % c for c in gen(len(B2)) if c[0] >= 501 or c[2] == 'all']
print('EXPECT_GONE=' + ','.join(gone))
