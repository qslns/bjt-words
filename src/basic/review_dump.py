"""전수 검수용 덤프: 기본 전용 카드의 모든 칸(뜻·한자음·이야기·포인트·바꿔 말하면·어원·짝·예문·풀이)
usage: review_dump.py OUTDIR [N_PER_FILE]"""
import json, re, sys, os
A = json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8'))
K = A['kanji']; byid = {w['id']: w for w in A['words']}
out = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 45
B = sorted([w for w in A['words'] if w.get('ord') is None], key=lambda w: w['bn'])
def rb(j): return re.sub(r'\[([^|\]]+)\|([^\]]*)\]', r'\1《\2》', j).replace('{', '⟨').replace('}', '⟩')
def tag(o): return f"No.{o['ord']+1}" if o.get('ord') is not None else f"B{o['bn']}"
for i in range(0, len(B), n):
    ch = B[i:i + n]
    with open(os.path.join(out, f'rv_{ch[0]["bn"]:03d}.txt'), 'w', encoding='utf-8') as f:
        for w in ch:
            f.write(f"#{w['bn']} {w['w']}({w['r']}) [{w['c']}] {w['m']} | ko={w['ko']} | hw={rb(w['hw'])}\n")
            f.write(f"  ST: {w['st']}\n  P: {w['p']}\n")
            f.write(f"  Y: {w['y']} | O: {w['o']} | PR: " + ', '.join(f"{byid[x]['w']}({tag(byid[x])} {byid[x]['m']})" for x in w['pr']) + '\n')
            ks = ' '.join(f"{c}={K[c]['h']}" for c in w['kj'] if c in K)
            if ks: f.write(f"  K: {ks}\n")
            for k, e in enumerate(w['e'], 1):
                f.write(f"  {k}) [{e['s']}] {rb(e['j'])} | {e['k']}\n")
                f.write('     g: ' + ' / '.join(f'{a}={b}' for a, b in e['g']) + '\n')
print('files', (len(B) + n - 1) // n)
