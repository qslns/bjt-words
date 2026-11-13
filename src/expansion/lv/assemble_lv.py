#!/usr/bin/env python3
"""N3·N2 칸 한 부(500개) 합치기 준비(11/14): 순위 FROM~TO의 카드를 모아 append_cards 입력을 만듦
- 앱 카드(A) → lvset {id, jl, jn}
- 복원(R)·새(N) → 최종 카드 파일들(--final, jsonl 여러 개)에서 찾음 → cards.jsonl + order.json {id, jl, jn}
- 이미 앞 부에서 jl·jn이 붙은 카드는 건드리지 않음(데이터에 jn 있음)
usage: python3 assemble_lv.py SEC FROM TO OUTDIR --final F1.jsonl F2.jsonl …"""
import sys, json, os, argparse
ap = argparse.ArgumentParser(); ap.add_argument('sec'); ap.add_argument('a', type=int); ap.add_argument('b', type=int); ap.add_argument('out')
ap.add_argument('--final', nargs='+', required=True); ap.add_argument('--data', default='/home/claude/work/build/data_app.json')
A = ap.parse_args()
E = '/home/claude/work/expansion'
L = json.load(open(E + '/lv/lv_order.json', encoding='utf-8'))[A.sec]
LV = int(A.sec[1])
D = json.load(open(A.data, encoding='utf-8')); W = {w['id']: w for w in D['words']}
fin = {}
for f in A.final:
    for l in open(f, encoding='utf-8'):
        if l.strip():
            c = json.loads(l)
            if c['id'] in fin and json.dumps(fin[c['id']], sort_keys=True) != json.dumps(c, sort_keys=True): sys.exit('같은 id 다른 카드 두 파일: %s' % c['id'])
            fin[c['id']] = c
os.makedirs(A.out, exist_ok=True)
lvset, order, cards, miss = [], [], [], []
for x in L[A.a - 1:A.b]:
    if x['kind'] == 'A':
        w = W[x['id']]
        if w.get('jn') is not None:
            if (w['jl'], w['jn']) != (LV, x['jn']): sys.exit('이미 다른 번호: %s' % x['id'])
            continue
        lvset.append({'id': x['id'], 'jl': LV, 'jn': x['jn']})
    else:
        if x['id'] in W: sys.exit('이미 앱에 있는 복원·새 카드: %s' % x['id'])
        if x['id'] not in fin: miss.append((x['jn'], x['id'], x['w'])); continue
        c = fin[x['id']]
        if c['w'] != x['w'] and not c['w'].replace('〜', '') == x['w'].replace('〜', ''): print('표제 바뀜(검수):', x['id'], x['w'], '→', c['w'])
        cards.append(c); order.append({'id': x['id'], 'jl': LV, 'jn': x['jn']})
if miss: sys.exit('최종 카드 없음 %d: %s' % (len(miss), miss[:20]))
with open(A.out + '/cards.jsonl', 'w', encoding='utf-8') as o:
    for c in cards: o.write(json.dumps(c, ensure_ascii=False) + '\n')
json.dump(order, open(A.out + '/order.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(lvset, open(A.out + '/lvset.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(A.sec, A.a, A.b, '· 앱 카드에 번호', len(lvset), '· 새로 넣을 카드', len(cards))
