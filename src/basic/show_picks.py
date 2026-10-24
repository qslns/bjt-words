import json, sys
L = json.load(open('/home/claude/work/basic/list.json', encoding='utf-8'))
P = json.load(open('/home/claude/work/basic/sent_pick.json', encoding='utf-8'))
a, b = int(sys.argv[1]), int(sys.argv[2])
for o in L:
    if 'share' in o or not (a <= o['bn'] <= b): continue
    ps = P.get(str(o['bn']), [])
    if not ps: continue
    print(f"#{o['bn']} {o['w']}({o['r']}) {o['m']}")
    for i, x in enumerate(ps):
        print(f"   {i+1}. {x['p']}")
