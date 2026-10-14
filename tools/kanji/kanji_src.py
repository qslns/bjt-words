"""한자 950자 자료 (연상 쓰기용 시트 + 앱 데이터 원본)
- 단어 속 읽기를 기본 읽기로 정리: 음독(히라가나) / 훈독(어간(오쿠리가나)) · 촉음화·연탁·반탁·연용형(とり←と(る))
- 순서: 기본+본편1500 단어 중 이 한자를 쓰는 단어 수 많은 순, 같으면 공부 순서(기본 번호 → 본편 번호)에서 먼저 나온 순"""
import json, re, collections, sys
D = json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8'))
K, W = D['kanji'], D['words']
byid = {w['id']: w for w in W}
scope = [w for w in W if w.get('bn') or w['id'] < 9000]
study_rank = {}
for w in sorted([w for w in scope if w.get('bn')], key=lambda w: w['bn']): study_rank.setdefault(w['id'], len(study_rank))
for w in sorted([w for w in scope if w['id'] < 9000], key=lambda w: w['ord']): study_rank.setdefault(w['id'], len(study_rank))
def k2h(s): return ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in s)
VOICE = str.maketrans('かきくけこさしすせそたちつてとはひふへほ', 'がぎぐげござじずぜぞだぢづでどばびぶべぼ')
HALF = str.maketrans('はひふへほ', 'ぱぴぷぺぽ')
IROW = dict(zip('うくぐすつぬぶむる', 'いきぎしちにびみり'))
EXTRA = {'慶': [('kun', 'よろこ', 'ぶ')], '上': [('kun', 'うわ', '')], '度': [('on', 'たく', '')], '次': [('kun', 'つぎ', '')]}   # 사전 자료에 빠진 읽기
SPLIT = {'小売': [('小', 'こ'), ('売', 'うり')], '反応': [('反', 'はん'), ('応', 'のう')], '最寄': [('最', 'も'), ('寄', 'より')]}
KR_OVERRIDE = {87: [['中', 'じゅう']], 451: [['何', 'なに']]}
SANDHI = {('応', 'のう'): ('おう', 'on', 'のう'), ('最', 'も'): ('も', 'kun', '')}
def bases(c):
    k = K[c]; out = [('on', k2h(o), '') for o in k['on']]
    for x in k['kun']:
        m = re.match(r'^([^()（）]+)(?:[(（]([^)）]*)[)）])?', x.replace('-', '').replace('.', ''))
        if m: out.append(('kun', m.group(1), m.group(2) or ''))
    return out + EXTRA.get(c, [])
def forms(kind, stem, ok):
    fs = {stem}
    if kind == 'kun' and ok:
        if ok[-1] in IROW: fs.add(stem + ok[:-1] + IROW[ok[-1]])          # 연용형 명사 (取り, 割り, 話し)
        if ok[-1] in 'つるう': fs.add(stem + ok[:-1] + 'っ')                 # 勝って, 切って
        if ok.endswith('る') and len(ok) >= 2: fs.add(stem + ok[:-1])        # 일단동사 (付け, 受け, 上げ)
    return fs
def okv(ok):
    """오쿠리가나가 단어 표기에 나타날 수 있는 모양들"""
    v = {ok}
    if ok:
        if ok[-1] in IROW: v.add(ok[:-1] + IROW[ok[-1]])
        if ok[-1] in 'つるう': v.add(ok[:-1] + 'っ')
        if ok.endswith('る'): v.add(ok[:-1])
        if ok.endswith('い'): v |= {ok[:-1] + x for x in ('く', 'か', 'さ', 'け')}
        if ok[-1] in 'うくぐすつぬぶむる': v |= {ok[:-1] + x for x in ('わ', 'か', 'が', 'さ', 'た', 'な', 'ば', 'ま', 'ら', 'え', 'け', 'げ', 'せ', 'て', 'ね', 'べ', 'め', 'れ', 'お', 'こ', 'ご', 'そ', 'と', 'の', 'ぼ', 'も', 'ろ', 'ん')}
    return v
def norm(c, r, fol=''):
    hits = []
    for kind, b, ok in bases(c):
        disp = b + ('(' + ok + ')' if ok else '')
        fs = forms(kind, b, ok)
        hit = None
        if r in fs: hit = (disp, kind, '' if r == b else r)
        else:
            for f in fs:
                if len(f) > 1 and kind == 'on' and f[-1] in 'つちくき' and r == f[:-1] + 'っ': hit = (disp, kind, r); break
                if r[0] != f[0] and (r == f[:1].translate(VOICE) + f[1:] or r == f[:1].translate(HALF) + f[1:]): hit = (disp, kind, r); break
                if kind == 'on' and f[-1] in 'つちくき' and r[0] != f[0] and (r == f[:1].translate(VOICE) + f[1:-1] + 'っ' or r == f[:1].translate(HALF) + f[1:-1] + 'っ'): hit = (disp, kind, r); break
        if hit:
            # 오쿠리가나 일치 점수: 단어에서 한자 뒤에 오는 가나가 이 훈독의 오쿠리가나 모양과 맞는가
            sc = 0
            if kind == 'kun' and ok:
                rest = r[len(b):] if r.startswith(b) else ''
                tail = rest + fol
                sc = max((len(v) for v in okv(ok) if v and tail.startswith(v)), default=-1)
                if r == b and not fol: sc = -1
            elif kind == 'kun' and not ok:
                sc = 0.5 if not fol or r != b else 0.5
            else:
                sc = 0.5
            hits.append((sc, hit))
    if hits:
        hits.sort(key=lambda x: -x[0])
        return hits[0][1]
    return r, '?', ''
data = {}
for w in scope:
    for c in dict.fromkeys(w.get('kj') or []):
        data.setdefault(c, {'words': [], 'reads': collections.Counter(), 'forms': collections.defaultdict(set), 'unk': [], 'wb': {}})
        data[c]['words'].append(w['id'])
    krs = []
    KR = KR_OVERRIDE.get(w['id'], w.get('kr') or [])
    for c, r in KR:
        if c == '々': continue
        if c in SPLIT: krs += [(a, b, '') for a, b in SPLIT[c]]; continue
        krs.append((c, r, None))
    s = w['w']; pos = 0; krs2 = []
    for c, r, f in krs:
        if f is None:
            i = s.find(c, pos)
            if i >= 0:
                j = i + len(c); fol = ''
                while j < len(s) and '\u3041' <= s[j] <= '\u309f': fol += s[j]; j += 1
                pos = i + len(c)
            else: fol = ''
        else: fol = f
        krs2.append((c, r, fol))
    for c, r, fol in krs2:
        if (c, r) in SANDHI: b, kind, f = SANDHI[(c, r)]
        else: b, kind, f = norm(c, r, fol)
        data[c]['reads'][(b, kind)] += 1
        data[c]['wb'].setdefault(w['id'], [b, r])
        if f: data[c]['forms'][(b, kind)].add(f)
        if kind == '?': data[c]['unk'].append((w['w'], r))
order = sorted(data, key=lambda c: (-len(data[c]['words']), min(study_rank[i] for i in data[c]['words'])))
out = []
for n, c in enumerate(order, 1):
    d = data[c]; k = K[c]
    ws = sorted(d['words'], key=lambda i: study_rank[i])
    out.append({'n': n, 'c': c, 'h': k['h'], 'strokes': k['n'],
                'reads': [[b, kind, cnt, sorted(d['forms'].get((b, kind), []))] for (b, kind), cnt in d['reads'].most_common()],
                'dict_on': [k2h(o) for o in k['on']], 'dict_kun': k['kun'], 'words': ws, 'unk': d['unk'], 'wb': {str(i): v for i, v in d['wb'].items()}})
json.dump(out, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False)
print('kanji', len(out), 'unmatched', sum(len(x['unk']) for x in out), [u for x in out for u in x['unk']])
print('no reading in deck (only 熟字訓 words):', [(x['c'], [byid[i]['w'] for i in x['words']]) for x in out if not x['reads']])
import itertools
cnts = [len(x['words']) for x in out]
for a, b in ((0, 100), (100, 300), (300, 600), (600, 950)): print(f'{a+1}-{b}: words/kanji {sum(cnts[a:b])/len(cnts[a:b]):.1f}')
