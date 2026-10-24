import json, sys
L = json.load(open('/home/claude/work/basic/list.json', encoding='utf-8'))
P = json.load(open('/home/claude/work/basic/sent_pick.json', encoding='utf-8'))
dec = {}
for ln in open('/home/claude/work/basic/pick_dec.tsv', encoding='utf-8'):
    if ln.startswith('#') or not ln.strip(): continue
    bn, k = ln.rstrip('\n').split('\t')[:2]
    dec[int(bn)] = [] if k == '-' else [int(x) for x in k.split(',')]
keep = {}; need = {}
for o in L:
    if 'share' in o: continue
    bn = o['bn']; ps = P.get(str(bn), [])
    ks = dec.get(bn, list(range(1, min(2, len(ps)) + 1)))
    ks = [k for k in ks if k <= len(ps)]
    keep[bn] = [ps[k-1] for k in ks]
    need[bn] = 2 - len(ks)
json.dump(keep, open('/home/claude/work/basic/keep.json', 'w', encoding='utf-8'), ensure_ascii=False)
tot = sum(need.values()); c0 = sum(1 for v in need.values() if v == 2); c1 = sum(1 for v in need.values() if v == 1)
print('new sentences needed', tot, 'cards needing 2:', c0, 'needing 1:', c1)
print('kept', sum(len(v) for v in keep.values()))
