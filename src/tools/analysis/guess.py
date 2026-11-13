"""501~1500 단어를 '유추 가능성' 종류로 나눠 등장 비율 보기 (usage: python3 guess.py DATA KANJI NAME=TXT ...)"""
import os
import sys, json, re, runpy, collections
data, kfile, *specs = sys.argv[1:]
sys.argv = ['rankbands.py', data]
g = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rankbands.py'), run_name='lib')
W = g['W']; count = g['count']
K950 = set(k['c'] for k in json.load(open(kfile, encoding='utf-8')))
KJ = re.compile(r'[一-鿿々]'); KANA_H = re.compile(r'[぀-ゟ]'); KATA = re.compile(r'^[゠-ヿー・]+$')
def first_mean(m): return re.split(r'[,，(（·/;]', m)[0].strip()
def kind(w):
    h = re.sub(r'[（(].*?[)）]', '', w['w']).strip('〜～ ')
    if KATA.match(h): return 'katakana'
    if not KJ.search(h): return 'kana'
    if KANA_H.search(h): return 'mixed'          # 落ち込む 같은 和語(한자+가나)
    ko = (w.get('ko') or '').strip()
    transp = bool(ko) and first_mean(w['m']) == ko
    allk = all(ch in K950 for ch in KJ.findall(h))
    return ('kango-same' if transp else 'kango-diff') + ('' if allk else '(950밖 한자)')
groups = {'501~1000': (500, 1000), '1001~1500': (1000, 1500)}
mem = {gname: [w for w in W if w.get('ord') is not None and 'bn' not in w and lo <= w['ord'] < hi] for gname, (lo, hi) in groups.items()}
for gname, ws in mem.items():
    print(f'== {gname}: 단어 수 기준', dict(collections.Counter(kind(w) for w in ws).most_common()))
for spec in specs:
    name, path = spec.split('=', 1)
    c, n = count([l.strip() for l in open(path, encoding='utf-8') if l.strip() and not l.startswith('@@')])
    for gname, ws in mem.items():
        occ = collections.Counter()
        for w in ws: occ[kind(w)] += c[w['id']]
        tot = sum(occ.values()) or 1
        print(f'{name:8} {gname}: 등장 기준', ' · '.join(f'{k} {100*v/tot:.0f}%' for k, v in occ.most_common()))
