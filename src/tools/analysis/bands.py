"""단어장 구간별(기본/1-500/501-1000/1001-1500) 등장 분포 — 섹션별 집계만 출력
usage: python3 bands.py DATA_JSON TXT_DIR"""
import sys, os, re, glob, json, collections
import fugashi
data, txtdir = sys.argv[1], sys.argv[2]
tg = fugashi.Tagger()
BANDS = ['basic', 'b1', 'b2', 'b3']
W = json.load(open(data, encoding='utf-8'))['words']
def band(w):
    if 'bn' in w: return 'basic'
    o = w['ord']; return 'b1' if o < 500 else 'b2' if o < 1000 else 'b3'
def toks(s):
    out = []; prev = None
    for t in tg(s):
        f = t.feature
        aux = f.pos2 == '非自立可能' and f.pos1 in ('動詞', '形容詞') and prev is not None and (
            (prev.pos1 == '助詞' and prev.pos2 == '接続助詞') or (f.lemma == '為る' and prev.pos1 == '名詞'))
        func = (f.pos1 in ('代名詞', '連体詞', '感動詞', '接続詞') or f.pos3 == '助数詞' or (f.lemma or '').endswith('-助数詞')
                or f.lemma in ('事', '物', '所', '為', '筈', '訳', '無い', '有り難う', 'さん', '御免'))
        out.append((f.lemma or t.surface, f.pos1, 'AUX' if aux else f.pos2, t.surface, func))
        prev = f
    return out
key2band, skipped = {}, 0
for w in W:
    h = re.sub(r'[（(].*?[)）]', '', w['w']).strip()
    if re.search(r'.[〜～].', h) or re.search(r'[…○]', h): skipped += 1; continue   # お〜になる 같은 문형
    h = h.strip('〜～')
    if not h: skipped += 1; continue
    for form in re.split(r'[・／/]', h):
        k = tuple(x[0] for x in toks(form))
        if not k: continue
        b = band(w)
        if k not in key2band or BANDS.index(b) < BANDS.index(key2band[k]): key2band[k] = b
MAXL = max(len(k) for k in key2band)
CONTENT = {'名詞', '動詞', '形容詞', '形状詞', '副詞', '連体詞', '接続詞', '感動詞', '代名詞', '接頭辞', '接尾辞'}
JP = re.compile(r'[぀-ヿ一-鿿]')
def is_content(t):
    lem, p1, p2, s, _ = t
    return p1 in CONTENT and p2 not in ('固有名詞', '数詞', 'AUX') and lem != '御' and bool(JP.search(s))
JOIN = os.environ.get('JOIN', '1') == '1'
PART = {'L': '청해', 'LR': '청독해', 'R': '독해'}
occ = collections.defaultdict(collections.Counter)     # band -> part -> 등장 수
DBG = collections.defaultdict(collections.Counter)
cov = collections.defaultdict(collections.Counter)     # part -> band/out -> 내용어 토큰 수
sub = collections.defaultdict(collections.Counter)     # 청독해 들리는/보이는
chars = collections.Counter()
for f in sorted(glob.glob(os.path.join(txtdir, 'p*.txt'))):
    pg = int(re.search(r'p(\d+)', f).group(1))
    sec, item = None, None
    raw = [l.strip() for l in open(f, encoding='utf-8')]
    lines = []   # 줄바꿈으로 잘린 본문 줄은 이어 붙임(긴 줄 + 문장부호로 안 끝남 + 다음 줄이 일본어로 시작)
    for l in raw:
        if (JOIN and lines and l and not l.startswith('@@') and not lines[-1].startswith('@@') and len(lines[-1]) >= 14
                and not re.search(r'[。！？!?」』）)：:]$', lines[-1]) and JP.match(l[0])):
            lines[-1] += l
        else: lines.append(l)
    for line in lines:
        m = re.match(r'@@\s*(LR|L|R)([123])\s+(\d+)', line)
        if m: sec, item = m.group(1), int(m.group(3)); continue
        if not line or sec is None or item == 0: continue
        part = PART[sec]; chars[part] += len(line)
        ts = toks(line); i = 0
        while i < len(ts):
            hit = None
            for L in range(min(MAXL, len(ts) - i), 0, -1):
                k = tuple(t[0] for t in ts[i:i + L])
                if k in key2band and any(is_content(t) for t in ts[i:i + L]): hit = (key2band[k], L); break
            if hit:
                b, L = hit; occ[b][part] += 1; DBG[(part, b)][''.join(t[3] for t in ts[i:i + L])] += 1
                n = sum(1 for t in ts[i:i + L] if is_content(t)); cov[part][b] += n
                if sec == 'LR': sub['들림' if pg >= 88 else '보임'][b] += n
                i += L
            else:
                if is_content(ts[i]):
                    c = 'func' if ts[i][4] else 'out'
                    cov[part][c] += 1; DBG[(part, c)][ts[i][0]] += 1
                    if sec == 'LR': sub['들림' if pg >= 88 else '보임'][c] += 1
                i += 1
parts = ['청해', '청독해', '독해']
print('글자 수', dict(chars), '| 문형이라 뺀 표제어', skipped)
print('\n[구간별 등장 → 섹션 분포 %]  (등장 횟수)')
for b in BANDS + ['func', 'out', 'all']:
    if b == 'all': row = collections.Counter({p: sum(cov[p].values()) for p in parts})
    elif b in ('out', 'func'): row = collections.Counter({p: cov[p][b] for p in parts})
    else: row = occ[b]
    tot = sum(row[p] for p in parts)
    print(f'{b:6}', ' '.join(f'{p} {100*row[p]/max(tot,1):5.1f}%' for p in parts), f'(n={tot})')
print('\n[섹션별 내용어 중 구간 비중 %]')
for p in parts:
    tot = sum(cov[p].values()) or 1
    print(f'{p:4}', ' '.join(f'{b} {100*cov[p][b]/tot:5.1f}%' for b in BANDS + ['func', 'out']), f'(내용어 {tot})')
for k in ('들림', '보임'):
    tot = sum(sub[k].values()) or 1
    print(f'청독해-{k}', ' '.join(f'{b} {100*sub[k][b]/tot:5.1f}%' for b in BANDS + ['func', 'out']), f'(내용어 {tot})')

if os.environ.get('DEBUG'):
    for (p, b), c in sorted(DBG.items()): print('DBG', p, b, c.most_common(int(os.environ['DEBUG'])))
