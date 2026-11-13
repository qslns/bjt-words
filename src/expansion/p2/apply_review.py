# P2-4 검수 반영: cards/p2w*.jsonl + review/p2r*.tsv → cards_final.jsonl
import json, glob, re, os, sys
D = os.path.dirname(os.path.abspath(__file__))
fs = sorted(glob.glob(D + '/cards/p2w*.jsonl'), key=lambda f: int(re.search(r'p2w(\d+)', f).group(1)))
C = [json.loads(l) for f in fs for l in open(f, encoding='utf-8') if l.strip()]
by = {c['id']: c for c in C}
n = 0; bad = []
for t in sorted(glob.glob(D + '/review/p2r*.tsv')):
    for line in open(t, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line or line.startswith('#') or line.startswith('id\t'): continue
        p = line.split('\t')
        if len(p) < 5: bad.append((t, line[:60])); continue
        i, f, cur, sug, why = p[0], p[1], p[2], p[3], '\t'.join(p[4:])
        try: c = by[int(i)]
        except (ValueError, KeyError): bad.append((t, line[:60])); continue
        m = re.fullmatch(r'([jkg])(\d)', f)
        if m:
            k, e = m.group(1), int(m.group(2))
            while len(c['e']) <= e: c['e'].append({'s': c['e'][-1]['s'], 'j': '', 'k': '', 'g': []})
            c['e'][e][k] = json.loads(sug) if k == 'g' else sug
            ms = re.search(r'장면 s를 ([a-z]+)', why)
            if ms and k == 'j': c['e'][e]['s'] = ms.group(1)
        elif f in ('kr', 'pr'): c[f] = json.loads(sug)
        elif f in ('r', 'm', 'p', 'y', 'o', 'ko', 'st', 'c'): c[f] = sug
        else: bad.append((t, line[:60])); continue
        n += 1
with open(D + '/cards_final.jsonl', 'w', encoding='utf-8') as o:
    for c in C: o.write(json.dumps(c, ensure_ascii=False) + '\n')
print('반영', n, '· 못 읽음', len(bad)); [print(' ', b) for b in bad]
