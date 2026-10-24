# 기본 카드용 예문을 기존 예문 3,280개에서 고르기 (토큰·읽기 일치 + 루비 경계 일치)
import json, re, sys, collections
sys.path.insert(0, '/home/claude/work')
from corpus import tagger, lemma_of
W = '/home/claude/work'
def k2h(s): return ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in s or '')
D = json.load(open(f'{W}/build/data_final.json', encoding='utf-8'))
L = json.load(open(f'{W}/basic/list.json', encoding='utf-8'))
byid = {w['id']: w for w in D['words']}
VOICE = dict(zip('かきくけこさしすせそたちつてとはひふへほ', 'がぎぐげござじずぜぞだぢづでどばびぶべぼ'))
def rvars(x):
    out = {x}
    if x and x[0] in VOICE: out.add(VOICE[x[0]] + x[1:])
    if x and x[0] in 'はひふへほ': out.add(dict(zip('はひふへほ', 'ぱぴぷぺぽ'))[x[0]] + x[1:])
    for y in list(out):
        if len(y) > 1 and y[-1] in 'つちくき': out.add(y[:-1] + 'っ')
    return out
# ---- 마크업 단위 분해: [(plain_start, plain_end, text_in_markup)]
def units(j):
    out = []; pos = 0; i = 0
    while i < len(j):
        c = j[i]
        if c in '{}': i += 1; continue
        if c == '[':
            m = re.match(r'\[([^|\]]+)\|([^\]]*)\]', j[i:])
            base = m.group(1)
            out.append((pos, pos + len(base), m.group(0))); pos += len(base); i += len(m.group(0)); continue
        out.append((pos, pos + 1, c)); pos += 1; i += 1
    return out
def plain(j): return re.sub(r'\[([^|\]]+)\|[^\]]*\]', r'\1', j).replace('{', '').replace('}', '')
def remark(j, a, b):
    us = units(j)
    starts = {u[0] for u in us}; ends = {u[1] for u in us}
    if a not in starts or b not in ends: return None
    out = ''
    for s, e, t in us:
        if s == a: out += '{'
        out += t
        if e == b: out += '}'
    return out
# ---- 문장 목록 + 토큰
S = []
for w in D['words']:
    for i, e in enumerate(w['e']):
        p = plain(e['j'])
        toks = []; pos = 0
        for t in tagger(p):
            a = p.find(t.surface, pos); a = a if a >= 0 else pos; b = a + len(t.surface); pos = b
            f = t.feature
            toks.append((a, b, t.surface, lemma_of(t), k2h(f.kana or ''), f.pos1, k2h(getattr(f, 'lForm', '') or '')))
        S.append({'wid': w['id'], 'i': i, 'p': p, 'toks': toks, 'e': e})
idx = collections.defaultdict(list)
lidx = collections.defaultdict(list)
for si, s in enumerate(S):
    for ti, tk in enumerate(s['toks']):
        idx[tk[3]].append((si, ti)); lidx[(tk[6], tk[5])].append((si, ti))
UNV = {v: k for k, v in VOICE.items()}; UNV.update(dict(zip('ぱぴぷぺぽ', 'はひふへほ')))
def norm(x): return ''.join(UNV.get(c, c) for c in x).replace('っ', 'つ')
def find(head, rd):
    h = head.replace('〜', '')
    iso = list(tagger(h))
    if not iso: return []
    base = k2h(rd)
    res = []
    conj = len(iso) == 1 and iso[0].feature.pos1 in ('動詞', '形容詞')
    if conj and not re.search(r'[\u4e00-\u9fff]', h):   # 가나 활용어(かける 등): 레마 읽기로 찾기
        for si, ti in lidx.get((base, iso[0].feature.pos1), []):
            tk = S[si]['toks'][ti]; res.append((si, tk[0], tk[1]))
        return res
    if conj:   # 활용어: 레마로 찾고 한자 부분 읽기 확인
        lem = lemma_of(iso[0])
        stem = re.sub(r'[ぁ-ゖ]+$', '', h); tail = h[len(stem):]
        rstem = base[:len(base) - len(tail)] if tail and base.endswith(tail) else base
        for si, ti in idx.get(lem, []):
            tk = S[si]['toks'][ti]
            if stem and re.search(r'[\u4e00-\u9fff]', stem):
                if not any(tk[4].startswith(v) for v in rvars(rstem)): continue
                if not S[si]['p'][tk[0]:tk[1]].startswith(stem): continue
            res.append((si, tk[0], tk[1]))
        return res
    # 비활용어: 표면형으로 찾고, 토큰 경계·읽기 확인
    for si, s in enumerate(S):
        p = s['p']; st = 0
        while True:
            a = p.find(h, st)
            if a < 0: break
            st = a + 1; b = a + len(h)
            tk = s['toks']
            starts = {t[0] for t in tk}; ends = {t[1] for t in tk}
            if a not in starts or b not in ends: continue
            red = ''.join(t[4] for t in tk if t[0] >= a and t[1] <= b)
            if re.search(r'[\u4e00-\u9fff]', h) and norm(red) != norm(base): continue
            res.append((si, a, b))
    return res
picks = {}; stat = collections.Counter()
for o in L:
    if 'share' in o: continue
    hits = find(o['w'], o['r'])
    cands = []
    for si, a, b in hits:
        s = S[si]
        if s['wid'] == o.get('share'): continue
        j2 = remark(s['e']['j'], a, b)
        if not j2: continue
        cands.append((si, a, b, j2))
    # 짧고 다양한 문장 우선(같은 출처 단어 중복 피함)
    cands.sort(key=lambda x: (abs(len(S[x[0]]['p']) - 24), S[x[0]]['wid']))
    sel = []; used = set()
    for c in cands:
        if S[c[0]]['wid'] in used: continue
        if any(S[c[0]]['p'] == S[x[0]]['p'] for x in sel): continue
        sel.append(c); used.add(S[c[0]]['wid'])
        if len(sel) == 3: break
    picks[o['bn']] = [{'wid': S[si]['wid'], 'i': S[si]['i'], 'a': a, 'b': b, 'j': j2, 'p': S[si]['p'], 'k': S[si]['e']['k']} for si, a, b, j2 in sel]
    stat[min(len(sel), 2)] += 1
json.dump(picks, open(f'{W}/basic/sent_pick.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('new cards', sum(stat.values()), '| 2+ picks', stat[2], '| 1 pick', stat[1], '| 0 picks', stat[0])
