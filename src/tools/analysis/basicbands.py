"""기본 구간(1~250/251~500/501~885) vs 본편 구간 한 단어당 빈도 (usage: python3 basicbands.py DATA NAME=TXT ...)"""
import sys, re, runpy, collections, glob, os
data, *specs = sys.argv[1:]
sys.argv = ['rankbands.py', data]
g = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rankbands.py'), run_name='lib')
W = g['W']; count = g['count']
B = {'기본 1~250': [w['id'] for w in W if 'bn' in w and w['bn'] <= 250],
     '기본 251~500': [w['id'] for w in W if 'bn' in w and 250 < w['bn'] <= 500],
     '기본 501~885': [w['id'] for w in W if 'bn' in w and w['bn'] > 500],
     'BJT S 1~347': [w['id'] for w in W if w.get('ord') is not None and 'bn' not in w and w['ord'] < 347],
     'BJT A 348~500': [w['id'] for w in W if w.get('ord') is not None and 'bn' not in w and 347 <= w['ord'] < 500],
     'BJT A 501~1000': [w['id'] for w in W if w.get('ord') is not None and 'bn' not in w and 500 <= w['ord'] < 1000]}
print('단어 수', {k: len(v) for k, v in B.items()})
for spec in specs:
    name, path = spec.split('=', 1)
    if os.path.isdir(path):
        lines = []
        for f in sorted(glob.glob(os.path.join(path, 'p*.txt'))):
            sec = None
            for l in open(f, encoding='utf-8'):
                m = re.match(r'@@\s*(LR|L|R)([123])\s+(\d+)', l.strip())
                if m: sec = int(m.group(3)); continue
                if sec and l.strip(): lines.append(l.strip())
    else: lines = [l.strip() for l in open(path, encoding='utf-8') if l.strip() and not l.startswith('@@')]
    c, n = count(lines)
    base = 1e5 * sum(c[i] for i in B['BJT A 501~1000']) / n / len(B['BJT A 501~1000'])
    tot = sum(c.values())
    out = []
    for k, ids in B.items():
        r = 1e5 * sum(c[i] for i in ids) / n / len(ids)
        out.append(f"{k} ×{r / base:.1f} (내용어의 {100 * sum(c[i] for i in ids) / n:.1f}%, 나온 단어 {100 * sum(1 for i in ids if c[i]) / len(ids):.0f}%)")
    print(f'{name}:\n   ' + '\n   '.join(out))
