import json, sys
L = json.load(open('/home/claude/work/basic/list.json', encoding='utf-8'))
K = json.load(open('/home/claude/work/basic/keep.json', encoding='utf-8'))
a, b = int(sys.argv[1]), int(sys.argv[2])
n = 0
for o in L:
    if 'share' in o or not (a <= o['bn'] <= b): continue
    ks = K.get(str(o['bn']), [])
    if len(ks) >= 2: continue
    n += 2 - len(ks)
    print(f"#{o['bn']} {o['w']}({o['r']}) {o['m']} [{o.get('c','')}] need{2-len(ks)}" + (f" | P: {o['p']}" if o.get('p') else ''))
    for x in ks: print('   =', x['p'])
print('total', n, file=sys.stderr)
