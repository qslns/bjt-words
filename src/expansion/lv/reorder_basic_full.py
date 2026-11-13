#!/usr/bin/env python3
"""기본 전체 재배열(11/13 22:35 사용자: '기본은 기본답게, BJT식 아니게, 진도 초기화 괜찮음')
순서 점수 = 일반 빈도(wordfreq zipf: 구어·자막·웹·뉴스) + N5 0.5 + (목록에 급이 안 맞은 인사·표현 0.25)
바뀌는 것: 단어 bn(1~1330 전부) + 한자 u 순서. 기본 장 진도는 전부 새로 시작(키가 바뀜). BJT(ord)는 그대로.
usage: python3 reorder_basic_full.py DATA_IN LV_ROWS DATA_OUT ORDER_OUT"""
import sys, json
sys.path.insert(0, '/home/claude/work/expansion/tools')
from append_cards import compute_u, dump
din, rowsp, dout, oout = sys.argv[1:5]
D = json.load(open(din, encoding='utf-8')); W = D['words']; byid = {w['id']: w for w in W}
R = {r['id']: r for r in json.load(open(rowsp, encoding='utf-8')) if r['kind'] == 'A'}
B = sorted([w for w in W if w.get('bn') is not None], key=lambda w: w['bn'])
assert [w['bn'] for w in B] == list(range(1, len(B) + 1))
def score(w):
    r = R[w['id']]; lv = r['lv']
    return r['wf'] + (0.5 if lv == 5 else 0.25 if lv not in (4, 5) else 0)
new = sorted(B, key=lambda w: (-score(w), w['bn']))
before = {w['id']: dump(w) for w in W}; kb = {c: dump(k) for c, k in D['kanji'].items()}
order = []
for i, w in enumerate(new):
    order.append({'id': w['id'], 'w': w['w'], 'old_bn': w['bn'], 'new_bn': i + 1, 'lv': R[w['id']]['lv'], 'wf': R[w['id']]['wf'], 'score': round(score(w), 3)})
for o in order: byid[o['id']]['bn'] = o['new_bn']
U = compute_u(W, D['kanji'])
for c, k in D['kanji'].items(): k['u'] = U[c]
for w in W:
    o = json.loads(before[w['id']])
    if 'bn' in o: o['bn'] = w['bn']
    assert dump(o) == dump(w), w['id']
nu = 0
for c, k in D['kanji'].items():
    o = json.loads(kb[c]); nu += o['u'] != k['u']; o['u'] = k['u']; assert dump(o) == dump(k), c
json.dump(D, open(dout, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(order, open(oout, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('bn 바뀐 단어', sum(o['old_bn'] != o['new_bn'] for o in order), '/', len(order), '· u 바뀐 한자', nu)
for a, b in ((0, 50), (50, 100), (450, 500), (950, 1000), (1280, 1330)):
    print(f'{a + 1}~{b}:', ' '.join(o['w'] for o in order[a:b]))
import collections
print('500개씩 급:', [dict(collections.Counter(o['lv'] for o in order[a:a + 500])) for a in (0, 500, 1000)])
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
print('EXPECT_GONE=' + ','.join('B:%d-%d:%s' % c for c in gen(len(B))))
