#!/usr/bin/env python3
"""4부~ 검수 반영 (11/13): 손보기 카드 + 검수 TSV → 최종 카드
쓰기: python3 apply_review_4.py --cards A.jsonl … --tsv R.tsv … --out OUT.jsonl [--skip SKIP.tsv]
- TSV 한 줄: id field current suggested reason (field = w r m t c ko kr p y o st pr · jN kN gN sN)
- suggested는 그 칸 전체 값(kr·pr·gN은 JSON). 예문 번호가 없으면 새로 붙임(jN과 kN·gN을 같이 줘야 함)
- SKIP.tsv: 반영하지 않을 줄 'id<TAB>field' (메인이 판정해서 뺀 것) — 이유는 그 파일에 적음
- 카드 순서는 --cards 파일 순서 그대로"""
import sys, json, re, argparse
ap = argparse.ArgumentParser()
ap.add_argument('--cards', nargs='+', required=True); ap.add_argument('--tsv', nargs='*', default=[])
ap.add_argument('--out', required=True); ap.add_argument('--skip')
a = ap.parse_args()
C = [json.loads(l) for f in a.cards for l in open(f, encoding='utf-8') if l.strip()]
by = {c['id']: c for c in C}
assert len(by) == len(C), '카드 id 겹침'
skip = set()
if a.skip:
    for l in open(a.skip, encoding='utf-8'):
        p = l.rstrip('\n').split('\t')
        if len(p) >= 2 and p[0].strip().isdigit(): skip.add((int(p[0]), p[1].strip()))
n = 0; bad = []; skipped = 0
for t in a.tsv:
    for line in open(t, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line.strip() or line.startswith('#') or line.startswith('id\t'): continue
        p = line.split('\t')
        if len(p) < 4: bad.append((t, line[:70])); continue
        i, f, sug = p[0].strip(), p[1].strip(), p[3]
        try: c = by[int(i)]
        except (ValueError, KeyError): bad.append((t, line[:70])); continue
        if (int(i), f) in skip: skipped += 1; continue
        m = re.fullmatch(r'([jkgs])(\d)', f)
        try:
            if m:
                k, e = m.group(1), int(m.group(2))
                while len(c['e']) <= e: c['e'].append({'s': c['e'][-1]['s'], 'j': '', 'k': '', 'g': []})
                c['e'][e][k] = json.loads(sug) if k == 'g' else sug
            elif f in ('kr', 'pr'): c[f] = json.loads(sug)
            elif f in ('w', 'r', 'm', 't', 'c', 'ko', 'p', 'y', 'o', 'st'): c[f] = sug
            else: bad.append((t, line[:70])); continue
        except json.JSONDecodeError:
            bad.append((t, 'JSON ' + line[:70])); continue
        n += 1
empty = [(c['id'], i) for c in C for i, e in enumerate(c['e']) if not e['j'] or not e['k']]
with open(a.out, 'w', encoding='utf-8') as o:
    for c in C: o.write(json.dumps(c, ensure_ascii=False) + '\n')
print('카드', len(C), '· 반영', n, '· 뺀 줄', skipped, '· 못 읽음', len(bad), '· 빈 예문', empty)
for b in bad: print('  ', b)
