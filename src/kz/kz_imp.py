"""10/20 한자 읽기 중요도(BJT): 단어장 표제어 + 예문 후리가나에서 읽기마다 몇 번 나오는지 세서 순위·흘려보기·대표 소리를 정함.
usage: python3 kz_imp.py  → kz_imp.json
점수 = 10×(핵심 표제어 수: 기본 885 + 본편 1~1,000) + 3×(그 밖 표제어 수: 본편 1,001~1,500) + 1×(예문 속 등장 수, 같은 문장은 한 번)
외울 것(빨강, sk=0) = ①은 늘, ②는 점수 30 이상, ③은 80 이상(최대 3개). 나머지는 회색(sk=1, 그 읽기가 나오는 단어에서 익힘). っ꼴·같은 어간 훈독은 맨 뒤.
대표 소리(rep) = 빨간 읽기를 순위대로(10/21 사용자: 중요하지 않은 음독은 읽지 말 것)."""
import json, re, collections
KZ = '/home/claude/work/kz'
cards = json.load(open(KZ + '/kz_cards.json', encoding='utf-8')); C = {c['c']: c for c in cards}
for c in cards: c['kun'] = [k for k in c['kun'] if k.replace('(', '').replace(')', '') not in c['on']]   # 気: 훈독 き(음독과 같음) 빼기
d = json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8'))
W = [w for w in d['words'] if w.get('ord') is not None or w.get('bn') is not None]
DAK = str.maketrans('かきくけこさしすせそたちつてとはひふへほ', 'がぎぐげござじずぜぞだぢづでどばびぶべぼ')
HAN = str.maketrans('はひふへほ', 'ぱぴぷぺぽ')
def variants(r):
    out = {r}
    if r: out |= {r[0].translate(DAK) + r[1:], r[0].translate(HAN) + r[1:]}
    more = set()
    for x in out:
        if len(x) >= 2 and x[-1] in 'つくちき': more.add(x[:-1] + 'っ')
    return out | more
def kun_parts(k):
    m = re.match(r'^([^(（]+)[(（]([^)）]+)[)）]$', k)
    return (m.group(1), m.group(2)) if m else (k, '')
KANA = re.compile(r'^[ぁ-ゖー]+')
ROW = {}
for row in ('あいうえお', 'かきくけこ', 'がぎぐげご', 'さしすせそ', 'ざじずぜぞ', 'たちつてと', 'だぢづでど', 'なにぬねの', 'はひふへほ', 'ばびぶべぼ', 'ぱぴぷぺぽ', 'まみむめも', 'らりるれろ', 'わ'):
    for ch in row: ROW[ch] = row
IROW = dict(zip('うくぐすつぬぶむる', 'いきぎしちにびみり'))
def kun_forms(k):
    """훈독 하나가 실제 글에서 보일 수 있는 꼴들: (꼴, 점수) — 送り仮名 없는 낱말, 어간, 명사형(割り→わり), 촉음꼴(勝っ→かっ)"""
    stem, oku = kun_parts(k)
    out = []
    if not oku: out.append((stem, 100))
    else:
        out.append((stem, 20))
        if oku[-1] in IROW: out.append((stem + oku[:-1] + IROW[oku[-1]], 60))   # 5단 명사형: とる→とり
        if oku[:-1]: out.append((stem + oku[:-1], 55))                           # 1단·형용사 어간: うける→うけ
        out.append((stem + oku[:-1] + 'っ', 40))                                 # 촉음꼴: かつ→かっ, きる→きっ
    return out
def attribute(c, r, follow=''):
    """한자 c를 r로 읽었을 때 카드의 어느 읽기인지(('on'|'kun', 카드 표기)). follow = 바로 뒤 가나(送り仮名 판별)"""
    card = C[c]
    for o in card['on']:
        if r in variants(o): return ('on', o)
    best, bs = None, -1
    for k in card['kun']:
        stem, oku = kun_parts(k)
        for form, sc in kun_forms(k):
            if r not in variants(form): continue
            if form == stem and oku:   # 어간만 읽은 경우: 뒤 가나가 送り仮名와 맞으면 강하게
                head, last = oku[:-1], oku[-1]
                if head and follow.startswith(head) and len(follow) > len(head) and (ROW.get(follow[len(head)]) == ROW.get(last) or follow[len(head)] in 'っんい' or last == 'る'):
                    sc = 300 + len(oku)
                elif not head and follow and (ROW.get(follow[0]) == ROW.get(last) or follow[0] in 'っん' or (last == 'る' and follow[0] in 'らりるれろ')):
                    sc = 250
                elif follow.startswith(oku[:-1]) and oku[:-1]:
                    sc = 200 + len(oku)
            if sc > bs: best, bs = k, sc
    return ('kun', best) if best else (None, None)
def split(base, reading):
    """여러 한자 덩어리의 읽기를 한자마다 나누기(음독 후보 먼저)."""
    ks = list(base)
    if any(k not in C for k in ks): return None
    def cands(k):
        out = []
        for o in C[k]['on']:
            for v in variants(o): out.append((v, ('on', o), 0))
        for kk in C[k]['kun']:
            for form, sc in kun_forms(kk):
                for v in variants(form): out.append((v, ('kun', kk), 1 if sc >= 100 else (2 if sc >= 55 else 3)))
        seen, res = set(), []
        for v, tag, pr in sorted(out, key=lambda x: (-len(x[0]), x[2])):
            if v not in seen: seen.add(v); res.append((v, tag))
        return res
    def go(i, rest):
        if i == len(ks): return [] if rest == '' else None
        for v, tag in cands(ks[i]):
            if rest.startswith(v):
                sub = go(i + 1, rest[len(v):])
                if sub is not None: return [tag] + sub
        return None
    return go(0, reading)
hw_core = collections.defaultdict(collections.Counter); hw_all = collections.defaultdict(collections.Counter); sent = collections.defaultdict(collections.Counter)
miss_hw = collections.Counter()
for w in W:
    is_core = w.get('bn') is not None or (w.get('ord') or 9999) <= 1000
    head = w['w']; seen = set()
    for c, r in (w.get('kr') or []):
        if c not in C or (c, r) in seen: continue
        seen.add((c, r))
        i = head.find(c); follow = KANA.match(head[i + 1:]).group(0) if i >= 0 and KANA.match(head[i + 1:]) else ''
        t, rd = attribute(c, r, follow)
        if not t: miss_hw[(c, r)] += 1; continue
        hw_all[c][(t, rd)] += 1
        if is_core: hw_core[c][(t, rd)] += 1
SEG = re.compile(r'\[([^|\]]+)\|([^\]]*)\]')
sents = {}
for w in W:
    for e in w['e']: sents[e['j']] = 1
n_seg = n_ok = 0
for j in sents:
    s = j.replace('{', '').replace('}', '')
    for m in SEG.finditer(s):
        base, rd = m.group(1), m.group(2)
        if not rd or not all(ch in C for ch in base): continue
        n_seg += 1
        tail = s[m.end():m.end() + 8]; tail = tail.split('[')[0]
        follow = KANA.match(tail).group(0) if KANA.match(tail) else ''
        if len(base) == 1:
            t, r2 = attribute(base, rd, follow)
            if t: sent[base][(t, r2)] += 1; n_ok += 1
        else:
            sp = split(base, rd)
            if sp:
                n_ok += 1
                for k, tag in zip(base, sp): sent[k][tag] += 1
out = {}; stats = collections.Counter()
for c, card in C.items():
    rows = []
    for t, lst in (('on', card['on']), ('kun', card['kun'])):
        for i, x in enumerate(lst):
            a, b, s_ = hw_core[c][(t, x)], hw_all[c][(t, x)], sent[c][(t, x)]
            rows.append({'t': t, 'r': x, 'i': i, 'core': a, 'hw': b, 'sent': s_, 'score': 10 * a + 3 * (b - a) + s_})
    rows.sort(key=lambda z: (-z['score'], 0 if z['t'] == 'on' else 1, z['i']))
    # 10/21: 외울 것(빨강)만 고르기 — っ꼴과 '이미 외운 훈독과 어간이 같은 훈독'(上 あ(げる)→あ(がる))은 따로 외울 필요 없어 맨 뒤로
    stems = set(); main, tail = [], []
    for z in rows:
        if z['r'].endswith('っ'): tail.append(z); continue
        if z['t'] == 'kun':
            st = kun_parts(z['r'])[0]
            if st in stems: tail.append(z); continue
            stems.add(st)
        main.append(z)
    rows = main + tail
    for n, z in enumerate(rows, 1): z['rank'] = n
    # 빨강: ①은 늘, ②는 점수 30 이상(핵심 표제어 3개쯤), ③은 80 이상일 때만(되도록 2개까지), 최대 3개. 끝의 っ꼴·같은 어간은 빼고
    must = []
    for z in main:
        k = len(must)
        if k == 0 or (k == 1 and z['score'] >= 30) or (k == 2 and z['score'] >= 80): must.append(z)
        else: break
    for z in rows: z['sk'] = 0 if z in must else 1
    ons = [z for z in rows if z['t'] == 'on']; kuns = [z for z in rows if z['t'] == 'kun']
    rep = [z['r'] for z in must]
    out[c] = {'on': [[z['r'], z['rank'], z['sk']] for z in ons], 'kun': [[z['r'], z['rank'], z['sk']] for z in kuns], 'rep': rep,
              'dbg': [(z['r'], z['core'], z['hw'], z['sent'], z['score']) for z in rows]}
    stats['must%d' % len(must)] += 1
    stats['kun_first' if rows and rows[0]['t'] == 'kun' else 'on_first'] += 1
    stats['skim'] += sum(z['sk'] for z in rows); stats['readings'] += len(rows)
json.dump(out, open(KZ + '/kz_imp.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('sentences', len(sents), 'segments', n_seg, 'attributed', n_ok, 'hw unattributed', dict(miss_hw))
print(dict(stats))
