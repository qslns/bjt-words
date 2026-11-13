"""단어장 번호 구간별 한 단어당 등장 빈도 (usage: python3 rankbands.py DATA NAME=TXT ...)"""
import sys, re, json, collections
import fugashi
data, *specs = sys.argv[1:]
tg = fugashi.Tagger()
W = json.load(open(data, encoding='utf-8'))['words']; byid = {w['id']: w for w in W}
def toks(s):
    o = []; prev = None
    for t in tg(s):
        f = t.feature
        aux = f.pos2 == '非自立可能' and f.pos1 in ('動詞', '形容詞') and prev is not None and ((prev.pos1 == '助詞' and prev.pos2 == '接続助詞') or (f.lemma == '為る' and prev.pos1 == '名詞'))
        o.append((f.lemma or t.surface, f.pos1, 'AUX' if aux else f.pos2, t.surface)); prev = f
    return o
def rank(w): return (0 if 'bn' in w else 1, w.get('bn', 0) if 'bn' in w else w['ord'])
key2id = {}
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
        ts = toks(line); i = 0; n += sum(1 for t in ts if is_c(t))
        while i < len(ts):
            hit = None
            for L in range(min(MAXL, len(ts) - i), 0, -1):
                k = tuple(t[0] for t in ts[i:i + L])
                if k in key2id and any(is_c(t) for t in ts[i:i + L]): hit = (key2id[k], L); break
            if hit: c[hit[0]] += 1; i += hit[1]
            else: i += 1
    return c, n
BANDS = [('S 1~347', 0, 347), ('A 348~500', 347, 500), ('A 501~750', 500, 750), ('A 751~1000', 750, 1000), ('B 1001~1500', 1000, 1500)]
members = {b: [w['id'] for w in W if w.get('ord') is not None and 'bn' not in w and lo <= w['ord'] < hi] for b, lo, hi in BANDS}
print('words per band (기본과 겹치는 것 제외):', {b: len(v) for b, v in members.items()})
for spec in specs:
    name, path = spec.split('=', 1)
    if not name.startswith('mock'): lines = [l.strip() for l in open(path, encoding='utf-8') if l.strip() and not l.startswith('@@')]
    else:   # 공식 모의: 연습 문제 제외
        lines = []; sec = None
        import glob, os
        for f in sorted(glob.glob(os.path.join(path, 'p*.txt'))):
            for l in open(f, encoding='utf-8'):
                m = re.match(r'@@\s*(LR|L|R)([123])\s+(\d+)', l.strip())
                if m: sec = int(m.group(3)); continue
                if sec and l.strip(): lines.append(l.strip())
    c, n = count(lines)
    rates = {b: 1e5 * sum(c[i] for i in ids) / n / len(ids) * 100 for b, ids in members.items()}   # 100단어당, 내용어 10만당
    base = rates['A 501~750'] * 0.5 + rates['A 751~1000'] * 0.5
    used = {b: sum(1 for i in ids if c[i]) / len(ids) for b, ids in members.items()}
    print(f'{name:8} (내용어 {n}):', ' | '.join(f'{b} {rates[b]:6.1f} (×{rates[b] / base:.1f}, 나온 단어 {100*used[b]:.0f}%)' for b in rates))
