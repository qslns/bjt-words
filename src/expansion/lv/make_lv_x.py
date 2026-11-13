#!/usr/bin/env python3
"""N3·N2 칸에 들어가는 4부 손본 카드(p34/cards4) → 검수 폴더 (11/13)
usage: python3 make_lv_x.py SEC FROM TO PREFIX [묶음 크기 40]   예: n3 501 1000 rvn3y
폴더마다 cards.jsonl(4부 손본 카드) · old_cards.json(옛 카드, 복원만) · sheet.json(4부 시트 항목)"""
import json, sys, os, glob
E = '/home/claude/work/expansion'; A = '/home/claude/agents'
sec, a, b, pre = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
size = int(sys.argv[5]) if len(sys.argv) > 5 else 40
L = json.load(open(E + '/lv/lv_order.json', encoding='utf-8'))
cards = {}
for f in sorted(glob.glob(E + '/p34/cards4/*.jsonl')):
    for l in open(f, encoding='utf-8'):
        if l.strip():
            c = json.loads(l); cards[c['id']] = c
sheet = {}
for f in glob.glob(A + '/p4r*/sheet.json') + [A + '/p4n/sheet.json']:
    for x in json.load(open(f, encoding='utf-8')):
        sheet[x.get('id') or x['old_card']['id']] = x
ids = [x['id'] for x in L[sec][a - 1:b] if x['kind'] != 'A' and x['id'] in cards]
miss = [i for i in ids if i not in sheet]
if miss: sys.exit('시트 항목 없음: %s' % miss)
made = []
for k in range(0, len(ids), size):
    ch = ids[k:k + size]; name = '%s%d' % (pre, k // size + 1); d = A + '/' + name
    if os.path.exists(d + '/cards.jsonl'): sys.exit('이미 있음: ' + name)
    os.makedirs(d, exist_ok=True)
    with open(d + '/cards.jsonl', 'w', encoding='utf-8') as o:
        for i in ch: o.write(json.dumps(cards[i], ensure_ascii=False) + '\n')
    json.dump([sheet[i]['old_card'] for i in ch if 'old_card' in sheet[i]], open(d + '/old_cards.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump([sheet[i] for i in ch], open(d + '/sheet.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    made.append((name, len(ch)))
print(sec, a, b, '4부 손본 카드', len(ids), made)
