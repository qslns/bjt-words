"""501~1500 중 한자로 유추 안 되는 말(한자+가나·뜻 다른 한자어·히라가나·가타카나) 빈도순 (usage: python3 nonguess.py DATA KANJI OUT BSD REPORTS DRILLS)"""
import os
import sys, json, re, runpy, collections
data, kfile, out, fd, fw, fm = sys.argv[1:7]
sys.argv = ['rankbands.py', data]
g = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rankbands.py'), run_name='lib')
W = g['W']; count = g['count']
gk = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'guess.py'), run_name='lib2', init_globals=None) if False else None
KJ = re.compile(r'[一-鿿々]'); KANA_H = re.compile(r'[぀-ゟ]'); KATA = re.compile(r'^[゠-ヿー・]+$')
def first_mean(m): return re.split(r'[,，(（·/;]', m)[0].strip()
def kind(w):
    h = re.sub(r'[（(].*?[)）]', '', w['w']).strip('〜～ ')
    if KATA.match(h): return '가타카나'
    if not KJ.search(h): return '히라가나'
    if KANA_H.search(h): return '한자+가나'
    ko = (w.get('ko') or '').strip()
    return '같은 한자어' if (ko and first_mean(w['m']) == ko) else '뜻 다른 한자어'
L = lambda p: [l.strip() for l in open(p, encoding='utf-8') if l.strip() and not l.startswith('@@')]
(cD, nD), (cW, nW), (cM, nM) = count(L(fd)), count(L(fw)), count(L(fm))
ws = [w for w in W if w.get('ord') is not None and 'bn' not in w and 500 <= w['ord'] < 1500]
rows = []
for w in ws:
    rD, rW, rM = (1e5 * c[w['id']] / n for c, n in ((cD, nD), (cW, nW), (cM, nM)))
    rows.append(dict(id=w['id'], w=w['w'], r=w['r'], m=w['m'], no=w['ord'] + 1, k=kind(w), s=0.25 * rD + 0.25 * rW + 0.5 * rM))
NG = ('한자+가나', '뜻 다른 한자어', '히라가나', '가타카나')
ng = sorted([r for r in rows if r['k'] in NG], key=lambda r: -r['s'])
tot_all = sum(r['s'] for r in rows); tot_ng = sum(r['s'] for r in ng)
print('501~1500 단어', len(rows), '| 유추 안 되는 말', len(ng), dict(collections.Counter(r['k'] for r in ng)), '| 등장 비중 %.0f%%' % (100 * tot_ng / tot_all))
for N in (50, 100, 150):
    top = ng[:N]; print(f'상위 {N}: 유추 안 되는 말 등장의 {100*sum(r["s"] for r in top)/tot_ng:.0f}%', dict(collections.Counter(r['k'] for r in top)), '| 501~1000 안:', sum(1 for r in top if r['no'] <= 1000))
json.dump(ng, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
for r in ng[:100]: print(f"{r['no']:4} {r['k']:6} {r['w']}({r['r']}) {r['m'][:18]}  s={r['s']:.1f}")
