"""JLPT(비공식 Tanos 목록) 급별로 단어장이 얼마나 덮는지 (usage: python3 jlptcov.py DATA OLD JLPT_DIR)"""
import os
import sys, re, json, csv, collections
import fugashi
data, oldp, jd = sys.argv[1:4]
tg = fugashi.Tagger()
W = json.load(open(data, encoding='utf-8'))['words']; OLD = json.load(open(oldp, encoding='utf-8'))
def forms(s):
    s = re.sub(r'[（(][^)）]*[)）]', '', s)
    out = []
    for f in re.split(r'[;；,，・/／、]', s):
        f = f.replace('〜', '').replace('～', '').replace(' ', '').replace('　', '').strip()
        if f: out.append(f)
    return out
def key(f): return tuple((t.feature.lemma or t.surface) for t in tg(f))
def keys_of(w):
    ks = set()
    for f in forms(w['w']): ks.add(f); ks.add(key(f))
    return ks
A = set(); B = set()
for w in W: A |= keys_of(w)
B = set(A)
for w in OLD: B |= keys_of(w)
res = {}
for lv in ('n5', 'n4', 'n3', 'n2', 'n1'):
    rows = list(csv.DictReader(open(f'{jd}/{lv}.csv', encoding='utf-8')))
    inA = inB = 0; missB = []
    for r in rows:
        fs = forms(r['expression']) or forms(r['reading'])
        ks = set(fs) | set(key(f) for f in fs)
        a = bool(ks & A); b = bool(ks & B)
        inA += a; inB += b
        if not b: missB.append(r['expression'])
    res[lv] = (len(rows), inA, inB, missB)
    print(f'{lv.upper()}: {len(rows)}개 — 지금 앱 {100*inA/len(rows):.0f}% · 지운 단어까지 {100*inB/len(rows):.0f}% · 빠진 것 {len(missB)}개 예: {" ".join(missB[:25])}')
tot = sum(res[l][0] for l in ('n5', 'n4', 'n3', 'n2')); a = sum(res[l][1] for l in ('n5', 'n4', 'n3', 'n2')); b = sum(res[l][2] for l in ('n5', 'n4', 'n3', 'n2'))
print(f'N5~N2 합계 {tot}개 — 지금 앱 {100*a/tot:.0f}% · 지운 단어까지 {100*b/tot:.0f}% · 빠진 것 {tot-b}개')
json.dump({l: res[l][3] for l in res}, open('./jlpt_missing.json', 'w', encoding='utf-8'), ensure_ascii=False)
