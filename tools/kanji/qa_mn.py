import json, re, glob, sys, collections
K = json.load(open('/home/claude/work/kanji_mn/kanji_src.json', encoding='utf-8'))
MN = []
for f in sorted(glob.glob('/home/claude/work/kanji_mn/mn/0*.tsv')):
    for ln, line in enumerate(open(f, encoding='utf-8').read().split('\n'), 1):
        if not line.strip(): continue
        p = line.split('\t')
        if len(p) != 2: print('BADLINE', f, ln, repr(line)); continue
        MN.append((p[0], p[1], f, ln))
print('lines', len(MN), 'kanji', len(K))
kc = [k['c'] for k in K]; mc = [m[0] for m in MN]
if kc != mc:
    for i, (a, b) in enumerate(zip(kc, mc)):
        if a != b: print('ORDER MISMATCH at', i + 1, a, b); break
    print('missing', set(kc) - set(mc), 'extra', set(mc) - set(kc))
dup = [c for c, n in collections.Counter(mc).items() if n > 1]
if dup: print('DUP', dup)
M = {m[0]: m for m in MN}
kata = re.compile(r'[ァ-ヺヽ-ヿ]')
def strip_paren(r):  # ま(ける) -> まける
    return r.replace('(', '').replace(')', '')
issues = collections.defaultdict(list)
for k in K:
    c = k['c']
    if c not in M: continue
    t = M[c][1]
    if kata.search(t): issues['katakana'].append((c, t))
    eus = re.findall(r'«([^»]+)»', t)
    if len(eus) != 1: issues['eu_count'].append((c, t)); continue
    eu = eus[0].split('·')
    hs = [x.strip() for x in re.split(r'[,、/]', k['h'])]
    heu = [x.split()[-1] for x in hs if x.split()]
    if not any(e in heu for e in eu): issues['eu_mismatch'].append((c, k['h'], eus[0]))
    # 읽기
    hira = set(re.findall(r'\(([぀-ゟ]+)\)', t))
    reads = k['reads']
    if not reads: continue
    tot = sum(r[2] for r in reads)
    for i, (base, kind, cnt, forms) in enumerate(reads):
        cand = {strip_paren(base)} | {strip_paren(x) for x in forms}
        stem = base.split('(')[0]
        found = any(any(cd in h for h in hira) for cd in cand) or (kind == 'kun' and any(h.startswith(stem) and len(stem) >= 2 for h in hira))
        found_any = found or any(cd in t for cd in cand)
        if not found_any:
            key = 'top_missing' if i == 0 else ('major_missing' if cnt / tot >= 0.2 else 'minor_missing')
            issues[key].append((c, base, cnt, tot, t))
    for h in hira:
        ok = False
        for (base, kind, cnt, forms) in reads:
            cand = {strip_paren(base)} | {strip_paren(x) for x in forms}
            if any(cd in h or h in cd for cd in cand) or h.startswith(base.split('(')[0]): ok = True
        if not ok: issues['hira_not_deck'].append((c, h, [r[0] for r in reads], t))
for key in ['katakana', 'eu_count', 'eu_mismatch', 'top_missing', 'major_missing', 'minor_missing', 'hira_not_deck']:
    print('==', key, len(issues[key]))
    for x in issues[key][:400 if '-a' in sys.argv else 40]: print('  ', x)
