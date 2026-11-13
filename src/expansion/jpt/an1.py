"""JPT 방향 논의용 빠른 집계(11/13): 카드 풀의 JLPT 급·일반 빈도(wordfreq zipf)
usage: python3 -I an1.py JLPT_DIR"""
import sys, re, json, csv, collections, statistics as st
import fugashi
from wordfreq import zipf_frequency as zf
jd = sys.argv[1]
tg = fugashi.Tagger()
W = json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8'))['words']
OLD = json.load(open('/home/claude/work/expansion/old_words_2312.json', encoding='utf-8'))
N32 = json.load(open('/home/claude/work/expansion/n3n2_missing.json', encoding='utf-8'))
try: P4C = {x.get('id') or x.get('src'): x for x in json.load(open('/home/claude/agents/p4c/out.json', encoding='utf-8'))}
except Exception as e: P4C = {}; print('p4c', e)
def forms(s):
    s = re.sub(r'[（(][^)）]*[)）]', '', s); out = []
    for f in re.split(r'[;；,，・/／、]', s):
        f = f.replace('〜', '').replace('～', '').replace(' ', '').replace('　', '').strip()
        if f: out.append(f)
    return out
def key(f): return tuple((t.feature.lemma or t.surface) for t in tg(f))
def keys_of(w):
    ks = set()
    for f in forms(w): ks.add(f); ks.add(key(f))
    return ks
LV = {}
for n in (5, 4, 3, 2, 1):
    for r in csv.DictReader(open(f'{jd}/n{n}.csv', encoding='utf-8')):
        for k in keys_of(r['expression']) | keys_of(r['reading']) if not r['expression'] else keys_of(r['expression']):
            LV.setdefault(k, n)   # 쉬운 급 먼저
def lv(w, r=None):
    c = [LV[k] for k in keys_of(w) if k in LV]
    return max(c) if c else 0
def z(w):
    fs = forms(w)
    return max((zf(f, 'ja') for f in fs), default=0)
def summ(name, rows):
    c = collections.Counter(r['lv'] for r in rows); zs = [r['z'] for r in rows]
    print(f"{name:<26} n={len(rows):<5} N5 {c[5]:<4} N4 {c[4]:<4} N3 {c[3]:<4} N2 {c[2]:<4} N1 {c[1]:<4} 없음 {c[0]:<4} | zipf 중앙 {st.median(zs):.2f} · ≥4.5 {sum(x>=4.5 for x in zs)} · ≥4.0 {sum(x>=4.0 for x in zs)} · ≥3.5 {sum(x>=3.5 for x in zs)}")
rows = []
for w in W:
    rows.append({'src': 'app', 'id': w['id'], 'w': w['w'], 'bn': w.get('bn'), 'ord': w.get('ord'), 't': w['t'], 'lv': lv(w['w']), 'z': z(w['w'])})
for w in OLD:
    rows.append({'src': 'old', 'id': w['id'], 'w': w['w'], 'lv': lv(w['w']), 'z': z(w['w'])})
drop = 0
for w in N32:
    d = P4C.get(w['id'])
    if d and d.get('action') == 'drop': drop += 1; continue
    rows.append({'src': 'new', 'id': w['id'], 'w': w['w'], 'lv': int(w['lv'][1]), 'z': z(w['w'])})
print('p4c keys sample', list(P4C.items())[:1], 'dropped', drop)
B = [r for r in rows if r.get('bn')]
print('== 기본(bn)')
summ('기본 1–500', [r for r in B if r['bn'] <= 500]); summ('기본 501–885', [r for r in B if 500 < r['bn'] <= 885]); summ('기본 886–1330', [r for r in B if r['bn'] > 885])
rest = sorted([r for r in B if r['bn'] > 500], key=lambda r: (-(r['lv'] == 5), -r['z']))
half = rest[:415]
print('501+ 830개를 (N5 먼저, 빈도순)으로 다시 세우면: 앞 415개 중 지금 886–1330에 있는 것', sum(r['bn'] > 885 for r in half), '· 지금 501–885에 있는 것', sum(r['bn'] <= 885 for r in half))
rest2 = sorted([r for r in B if r['bn'] > 500], key=lambda r: -r['z'])
print('빈도만으로: 앞 415개 중 886–1330', sum(r['bn'] > 885 for r in rest2[:415]))
print('예: 886+ 중 빈도 높은 것', [r['w'] for r in sorted([r for r in B if r['bn'] > 885], key=lambda r: -r['z'])[:25]])
print('예: 501–885 중 빈도 낮은 것', [r['w'] for r in sorted([r for r in B if 500 < r['bn'] <= 885], key=lambda r: r['z'])[:25]])
print('== 기본 아닌 풀')
M = [r for r in rows if r['src'] == 'app' and not r.get('bn')]
summ('BJT 1–500(기본 겹침 뺌)', [r for r in M if r['ord'] <= 500]); summ('BJT 501–1000', [r for r in M if 500 < r['ord'] <= 1000]); summ('BJT 1001–1500', [r for r in M if r['ord'] > 1000])
O = [r for r in rows if r['src'] == 'old']; N = [r for r in rows if r['src'] == 'new']
summ('복원 2,312', O); summ('새 N3·N2(뺀 것 제외)', N)
json.dump(rows, open('/home/claude/scratch/jpt/rows1.json', 'w', encoding='utf-8'), ensure_ascii=False)
# 거친 JPT 후보: 기본 아닌 것 중 (N3 이하) 또는 (N2·빈도≥4.0)
def tier(r):
    if r['lv'] in (5, 4, 3) and r['z'] >= 4.0: return 'S'
    if r['lv'] in (5, 4, 3) or (r['lv'] == 2 and r['z'] >= 4.0): return 'A'
    if r['lv'] == 2 or r['z'] >= 4.0: return 'B'
    return '-'
print('== 거친 JPT 후보(급·일반 빈도만, 교재 반영 전)')
for nm, R in (('앱 BJT 1–1500', M), ('복원(손보기 필요)', O), ('새로 쓸 것', N)):
    c = collections.Counter(tier(r) for r in R); print(f"{nm:<20} S {c['S']:<5} A {c['A']:<5} B {c['B']:<5} 해당 없음 {c['-']}")
