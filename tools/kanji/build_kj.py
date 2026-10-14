#!/usr/bin/env python3
"""한자 암기 자료(앱용) 만들기
입력: build/data_app.json (단어) + kanji_src.json (kanji_src.py 결과: 순서·읽기) + mn/0*.tsv (그림 연상)
출력: kanji_app.json  = [[한자, 음, 연상, 읽기[[읽기, 단어수]], 단어[[id, 이 단어에서의 읽기, 읽기 번호(-1=통째로)]]], ...]  (외우는 순서대로 950자)
검사: 한자 빠짐·중복·순서, «음», 가타카나, 연상 속 히라가나 읽기 — 하나라도 틀리면 멈춤"""
import json, glob, re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(sys.argv[1] if len(sys.argv) > 1 else '/home/claude/work/build/data_app.json', encoding='utf-8'))
SRC = json.load(open(HERE + '/kanji_src.json', encoding='utf-8'))
W = {w['id']: w for w in D['words']}
MN = {}
for f in sorted(glob.glob(HERE + '/mn/0*.tsv')):
    for ln, line in enumerate(open(f, encoding='utf-8').read().split('\n'), 1):
        if not line.strip(): continue
        p = line.split('\t')
        assert len(p) == 2, (f, ln, line)
        assert p[0] not in MN, ('dup', p[0])
        MN[p[0]] = p[1].strip()
order = [k['c'] for k in SRC]
assert len(order) == len(set(order)) == len(MN) == 950, (len(order), len(MN))
assert set(order) == set(MN), set(order) ^ set(MN)
assert set(order) == set(D['kanji']), set(order) ^ set(D['kanji'])
# 단어마다 한자 → 이 단어에서의 읽기 (kanji_src.py 와 같은 규칙)
SPLIT = {'小売': [('小', 'こ'), ('売', 'うり')], '反応': [('反', 'はん'), ('応', 'のう')], '最寄': [('最', 'も'), ('寄', 'より')]}
OVR = {87: [['中', 'じゅう']], 451: [['何', 'なに']]}
def word_reads(w):
    out = {}
    for c, r in OVR.get(w['id'], w.get('kr') or []):
        if c == '々': continue
        for a, b in (SPLIT[c] if c in SPLIT else [(c, r)]):
            out.setdefault(a, b)
    return out
kata = re.compile(r'[ァ-ヺヽ-ヿ]')
rows = []
for k in SRC:
    c = k['c']; mn = MN[c]
    eus = re.findall(r'«([^»]+)»', mn)
    assert len(eus) == 1, (c, mn)
    assert not kata.search(mn), (c, mn)
    heu = [x.split()[-1] for x in re.split(r'[,/]', k['h']) if x.split()]
    assert any(e in heu for e in eus[0].split('·')), (c, k['h'], eus[0])
    rd = [[r[0], r[2]] for r in k['reads']]
    ws = []
    bix = {r[0]: j for j, r in enumerate(k['reads'])}
    for i in k['words']:
        w = W[i]; form = word_reads(w).get(c, '')
        wb = k['wb'].get(str(i))
        if form:
            assert wb and wb[1] == form, (c, w['w'], form, wb)
            ws.append([i, form, bix[wb[0]]])
        else:
            assert not wb, (c, w['w'], wb)
            ws.append([i, '', -1])
    rows.append([c, eus[0], mn, rd, ws])
json.dump(rows, open(HERE + '/kanji_app.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
sz = len(json.dumps(rows, ensure_ascii=False, separators=(',', ':')).encode())
print('kanji_app.json', len(rows), 'kanji', sum(len(r[4]) for r in rows), 'word links', sz, 'bytes')
print('no-reading word links (熟字訓):', sum(1 for r in rows for x in r[4] if not x[1]))
