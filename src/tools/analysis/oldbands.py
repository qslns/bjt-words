"""지운 단어(옛 1501~3817) 한 단어당 빈도: 현재 단어장 + 옛 단어를 합쳐 긴 것 먼저 매칭 (usage: python3 oldbands.py DATA OLD NAME=TXT ...)"""
import os
import sys, re, json, collections
import fugashi
data, oldp, *specs = sys.argv[1:]
tg = fugashi.Tagger()
W = json.load(open(data, encoding='utf-8'))['words']; OLD = json.load(open(oldp, encoding='utf-8'))
for i, w in enumerate(sorted(OLD, key=lambda w: w.get('ord', 0))): w['_old'] = i + 1501; w['id'] = 900000 + i
ALL = W + OLD; byid = {w['id']: w for w in ALL}
def toks(s):
    o = []; prev = None
    for t in tg(s):
        f = t.feature
        aux = f.pos2 == '非自立可能' and f.pos1 in ('動詞', '形容詞') and prev is not None and ((prev.pos1 == '助詞' and prev.pos2 == '接続助詞') or (f.lemma == '為る' and prev.pos1 == '名詞'))
        o.append((f.lemma or t.surface, f.pos1, 'AUX' if aux else f.pos2, t.surface)); prev = f
    return o
def rank(w): return (0 if 'bn' in w else 1 if '_old' not in w else 2, w.get('bn', 0) if 'bn' in w else w.get('_old', w.get('ord', 0)))
key2id = {}
for w in ALL:
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
B = {'A 501~1000': [w['id'] for w in W if w.get('ord') is not None and 'bn' not in w and 500 <= w['ord'] < 1000],
     'B 1001~1500': [w['id'] for w in W if w.get('ord') is not None and 'bn' not in w and 1000 <= w['ord'] < 1500],
     '옛 1501~2000': [w['id'] for w in OLD if w['_old'] <= 2000], '옛 2001~2500': [w['id'] for w in OLD if 2000 < w['_old'] <= 2500],
     '옛 2501~3000': [w['id'] for w in OLD if 2500 < w['_old'] <= 3000], '옛 3001~3812': [w['id'] for w in OLD if w['_old'] > 3000]}
print('단어 수', {k: len(v) for k, v in B.items()})
res = {}
for spec in specs:
    name, path = spec.split('=', 1)
    c, n = count([l.strip() for l in open(path, encoding='utf-8') if l.strip() and not l.startswith('@@')])
    base = sum(c[i] for i in B['A 501~1000']) / len(B['A 501~1000'])
    print(name, ' | '.join(f"{k} ×{(sum(c[i] for i in ids) / len(ids)) / base:.2f} (내용어 {100 * sum(c[i] for i in ids) / n:.1f}%)" for k, ids in B.items()))
    for w in OLD: res.setdefault(w['id'], 0); res[w['id']] += 1e5 * c[w['id']] / n
json.dump({str(k): v for k, v in res.items()}, open('./old_rates.json', 'w'), ensure_ascii=False)
