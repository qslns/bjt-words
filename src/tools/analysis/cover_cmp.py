"""501~1000 전체 등장 중 '501~750 그대로' vs '골라 둔 250'이 덮는 비율 (usage: python3 cover_cmp.py DATA PICK NAME=TXT ...)"""
import os
import sys, json, runpy
data, pick, *specs = sys.argv[1:]
sys.argv = ['rankbands.py', data]           # rankbands의 매칭 함수만 재사용
g = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rankbands.py'), run_name='lib')
W = g['W']; count = g['count']
band = [w['id'] for w in W if w.get('ord') is not None and 'bn' not in w and 500 <= w['ord'] < 1000]
first = [w['id'] for w in W if w.get('ord') is not None and 'bn' not in w and 500 <= w['ord'] < 750]
P = json.load(open(pick, encoding='utf-8'))['ids']
for spec in specs:
    name, path = spec.split('=', 1)
    c, n = count([l.strip() for l in open(path, encoding='utf-8') if l.strip() and not l.startswith('@@')])
    tot = sum(c[i] for i in band)
    print(f'{name}: 501~750 그대로 {100*sum(c[i] for i in first)/tot:.0f}% · 골라 둔 250 {100*sum(c[i] for i in P)/tot:.0f}% (501~1000 전체 등장 {tot}회)')
