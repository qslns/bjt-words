import json, re, sys
D = json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8'))
a, b = int(sys.argv[1]), int(sys.argv[2])
only_new = len(sys.argv) > 3 and sys.argv[3] == 'new'
def rb(j): return re.sub(r'\[([^|\]]+)\|([^\]]*)\]', r'\1(\2)', j)
ws = sorted([w for w in D['words'] if w.get('bn') and a <= w['bn'] <= b], key=lambda w: w['bn'])
for w in ws:
    sh = w['id'] < 9000
    print(f"#{w['bn']} {w['w']}({w['r']}) [{w['c']}{'/'+w['t'] if sh else ''}] {w['m']}" + (f" | P: {w['p']}" if w.get('p') else '') + (f" | kr={w['kr']} ko={w['ko']}" if not sh else ' | SHARED No.' + str(w.get('ord'))))
    if sh: continue
    for i, e in enumerate(w['e']):
        print(f"  {i+1}){e['s']} {rb(e['j'])}\n     {e['k']}\n     g: " + ' · '.join(f'{x}={y}' for x, y in e['g']))
