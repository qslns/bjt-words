"""A등급 501~1000 중 청독해·독해용 250개 고르기 (공식 모의 안 씀)
usage: python3 select250.py DATA_JSON CHABSA_TXT BSD_TXT SAMPLE_TXT OUT_JSON [MOCK_DIR(겹침 개수만 셈)]"""
import sys, re, json, collections, math, glob, os
import fugashi
data, fw, fd, fs, fm, out = sys.argv[1:7]
mockdir = sys.argv[7] if len(sys.argv) > 7 else None
tg = fugashi.Tagger()
W = json.load(open(data, encoding='utf-8'))['words']
byid = {w['id']: w for w in W}
def toks(s):
    o = []; prev = None
    for t in tg(s):
        f = t.feature
        aux = f.pos2 == '非自立可能' and f.pos1 in ('動詞', '形容詞') and prev is not None and (
            (prev.pos1 == '助詞' and prev.pos2 == '接続助詞') or (f.lemma == '為る' and prev.pos1 == '名詞'))
        o.append((f.lemma or t.surface, f.pos1, 'AUX' if aux else f.pos2, t.surface)); prev = f
    return o
key2id = {}
def rank(w): return (0 if 'bn' in w else 1, w.get('bn', 0) if 'bn' in w else w['ord'])
for w in W:
    h = re.sub(r'[（(].*?[)）]', '', w['w']).strip()
    if re.search(r'.[〜～].', h) or re.search(r'[…○]', h): continue
    h = h.strip('〜～')
    for form in re.split(r'[・／/]', h):
        k = tuple(x[0] for x in toks(form))
        if k and (k not in key2id or rank(w) < rank(byid[key2id[k]])): key2id[k] = w['id']
MAXL = max(len(k) for k in key2id)
CONTENT = {'名詞', '動詞', '形容詞', '形状詞', '副詞', '連体詞', '接続詞', '感動詞', '代名詞', '接頭辞', '接尾辞'}
JP = re.compile(r'[぀-ヿ一-鿿]')
def is_c(t): return t[1] in CONTENT and t[2] not in ('固有名詞', '数詞', 'AUX') and t[0] != '御' and bool(JP.search(t[3]))
def count(lines):
    c = collections.Counter(); n = 0
    for line in lines:
        ts = toks(line); i = 0
        n += sum(1 for t in ts if is_c(t))
        while i < len(ts):
            hit = None
            for L in range(min(MAXL, len(ts) - i), 0, -1):
                k = tuple(t[0] for t in ts[i:i + L])
                if k in key2id and any(is_c(t) for t in ts[i:i + L]): hit = (key2id[k], L); break
            if hit: c[hit[0]] += 1; i += hit[1]
            else: i += 1
    return c, n
def lines_of(p): return [l.strip() for l in open(p, encoding='utf-8') if l.strip() and not l.startswith('@@')]
cW, nW = count(lines_of(fw)); cD, nD = count(lines_of(fd)); cS, nS = count(lines_of(fs)); cM2, nM2 = count(lines_of(fm))
print('content tokens: reports', nW, 'dialogue', nD, 'samples', nS, 'drills', nM2)
DOCS = {'graph', 'doc', 'mail', 'notice', 'report', 'news'}
CATF = {'graph': 1.1, 'doc': 1.1, 'deal': 1.1, 'money': 1.1, 'sales': 1.1, 'sch': 1.1, 'mtg': 1.1, 'tel': 0.8, 'keigo': 0.8}
def first_mean(m): return re.split(r'[,，(（·/;]', m)[0].strip()
KJ = re.compile(r'[\u4e00-\u9fff々]')
cand = [w for w in W if w.get('ord') is not None and 500 <= w['ord'] < 1000 and 'bn' not in w and w.get('t') == 'A' and KJ.search(w['w'])]
rows = []
for w in cand:
    rW = 1e5 * cW[w['id']] / nW; rD = 1e5 * cD[w['id']] / nD; rM = 1e5 * cM2[w['id']] / nM2
    sc = [e.get('s') for e in w.get('e', [])]
    docf = sum(1 for s in sc if s in DOCS) / max(1, len(sc))
    ko = (w.get('ko') or '').strip()
    transp = bool(ko) and first_mean(w['m']) == ko
    score = (0.2 * rW + 0.2 * rD + 0.6 * rM + 2.0) * (0.5 + 1.0 * docf) * CATF.get(w.get('c'), 1.0) * (1.3 if cS[w['id']] else 1.0)
    rows.append(dict(id=w['id'], w=w['w'], m=w['m'], ord=w['ord'] + 1, c=w.get('c'), rW=round(rW, 1), rD=round(rD, 1), rM=round(rM, 1), doc=round(docf, 2), transp=transp, smp=cS[w['id']], score=round(score, 2)))
rows.sort(key=lambda r: -r['score'])
DROP = {'願う', '者', 'お見えになる', '私ども', 'ご苦労様', '構いません', '調子', '存じ上げる', '足労', '〜てもよろしいでしょうか'}
rows = [r for r in rows if r['w'] not in DROP]
pick = rows[:250]
json.dump({'ids': [r['id'] for r in pick], 'rows': rows}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('candidates', len(cand), 'picked', len(pick), 'zero-evidence in pick', sum(1 for r in pick if r['rW'] == 0 and r['rD'] == 0))
print('pick cats', collections.Counter(r['c'] for r in pick).most_common())
print('transparent picked', sum(r['transp'] for r in pick), 'of', sum(r['transp'] for r in rows))
# 고른 단어가 등장 빈도로 얼마나 덮는지(편향 없는 글 기준)
tot = lambda key: sum(r[key] for r in rows); pk = lambda key: sum(r[key] for r in pick)
print('share of band occurrences covered by pick: reports %.0f%% dialogue %.0f%%' % (100 * pk('rW') / max(1e-9, tot('rW')), 100 * pk('rD') / max(1e-9, tot('rD'))))
if mockdir:
    ids = set(r['id'] for r in pick); allc = set(r['id'] for r in rows)
    ml = []
    for f in sorted(glob.glob(os.path.join(mockdir, 'p*.txt'))):
        sec = None
        for l in open(f, encoding='utf-8'):
            m = re.match(r'@@\s*(LR|L|R)([123])\s+(\d+)', l.strip())
            if m: sec = (m.group(1), int(m.group(3))); continue
            if sec and sec[0] in ('LR', 'R') and sec[1] != 0 and l.strip(): ml.append(l.strip())
    cM, nM = count(ml)
    print('MOCK(LR+R) overlap: picked types', sum(1 for i in ids if cM[i]), '/ band types in mock', sum(1 for i in allc if cM[i]), '| occurrences picked', sum(cM[i] for i in ids), '/ band', sum(cM[i] for i in allc))
