#!/usr/bin/env python3
"""N3·N2 칸 순서(중요도) + 기본 501~ 재배열 (11/13 페이지)
급: JLPT 비공식 목록(Tanos, github jamsinclair/open-anki-jlpt-decks src/n1~5.csv) — 표기+읽기로 맞춤(읽기가 다르면 다른 말)
중요도 imp = (일반 빈도 wf + 신문 빈도 nz) / 2
  wf = wordfreq zipf(일본어, 구어·자막·웹·위키·뉴스 섞임)
  nz = JMdict nfXX(마이니치 신문 빈도 순위, 500개 단위) → C − log10(순위) (C는 두 값이 다 있는 말로 맞춤). nf 없음 = 신문 상위 24,000 밖 → min(wf, C − log10(30000))
usage: python3 -I rank_lv.py JLPT_DIR OUT_DIR"""
import sys, os, re, json, csv, sqlite3, math, statistics as st, collections
sys.path.insert(0, '/home/claude/work/expansion/tools')
from cardlib import hira, is_kanji
from wordfreq import zipf_frequency as zf
JD, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
E = '/home/claude/work/expansion'
W = json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8'))['words']
OLD = json.load(open(E + '/old_words_2312.json', encoding='utf-8'))
RO = {x['id']: x for x in json.load(open(E + '/restore_order.json', encoding='utf-8'))}
P4S = json.load(open(E + '/p34/p4_scored.json', encoding='utf-8'))
P4Z = {x['id']: x for x in json.load(open(E + '/p34/p4_zero_input.json', encoding='utf-8'))}
P4ZF = json.load(open(E + '/p34/p4_zero_final.json', encoding='utf-8'))
IDS = json.load(open(E + '/p34/p4_ids.json', encoding='utf-8'))
DROP_R = {3808, 807, 1420, 1423, 1599, 2219, 3521}
DROP_N = {'Jn2-1553', 'Jn2-1509', 'Jn3-739'}
def clean_w(w): return re.sub(r'[〜～\s　]', '', w)
def clean_r(r): return hira(re.sub(r'[〜～\s　()（）]', '', r))
# ---- JLPT 목록
def forms(s):
    s = re.sub(r'[（(][^)）]*[)）]', '', s or '')
    return [f.strip() for f in re.split(r'[;；,，・/／、]', s) if f.strip()]
EXACT = {}; BYR = collections.defaultdict(list)
for n in (5, 4, 3, 2, 1):
    for row in csv.DictReader(open(f'{JD}/n{n}.csv', encoding='utf-8')):
        ex = [clean_w(f) for f in forms(row['expression'])] or [clean_w(f) for f in forms(row['reading'])]
        rd = [clean_r(f) for f in forms(row['reading'])] or [clean_r(f) for f in ex]
        for e in ex:
            for r in rd:
                rs = [r] + ([r[:-2]] if r.endswith('する') and not e.endswith('する') and len(r) > 2 else [])   # 목록 읽기 'せいかつする' → せいかつ
                for r2 in rs:
                    EXACT.setdefault((e, r2), n)
                    BYR[r2].append((e, n))
def kseq(s): return ''.join(c for c in s if is_kanji(c) or c == '々')
def level(w, r):
    w, r = clean_w(w), clean_r(r)
    if (w, r) in EXACT: return EXACT[(w, r)], 'exact'
    if not kseq(w):   # 가나 표제: 같은 읽기의 목록 항목
        c = [n for e, n in BYR.get(hira(w), []) if hira(e) == hira(w) or kseq(e)]
        if c: return max(c), 'kana'
        c = [n for e, n in BYR.get(hira(w) + 'に', [])]   # 목록 'すぐに' ↔ 카드 'すぐ'
        if c: return max(c), 'kana+に'
        return 0, ''
    c = [n for e, n in BYR.get(r, []) if kseq(e) == kseq(w)]   # 送り仮名 차이(取り替える/取替える)
    if c: return max(c), 'okuri'
    return 0, ''
# ---- JMdict 신문 빈도
DB = '/usr/local/lib/python3.13/site-packages/jamdict_data/jamdict.db'
c = sqlite3.connect(DB)
KP = collections.defaultdict(list); NP = collections.defaultdict(list)
for kid, t in c.execute('select kid, text from KJP'): KP[kid].append(t)
for kid, t in c.execute('select kid, text from KNP'): NP[kid].append(t)
KJ = collections.defaultdict(list)   # 표기 → [(idseq, pri)]
for i, q, t in c.execute('select ID, idseq, text from Kanji'): KJ[t].append((q, KP.get(i, [])))
KN = collections.defaultdict(list); KNQ = collections.defaultdict(list)
for i, q, t in c.execute('select ID, idseq, text from Kana'):
    KN[hira(t)].append((q, NP.get(i, []))); KNQ[q].append(hira(t))
def nfv(pris):
    v = [int(p[2:]) for p in pris if re.fullmatch(r'nf\d\d', p)]
    return min(v) if v else None
def nf_of(w, r):
    w, r = clean_w(w), clean_r(r); best = None
    if kseq(w):
        for q, pr in KJ.get(w, []):
            if r in KNQ.get(q, []):
                v = nfv(pr); best = v if best is None or (v is not None and v < best) else best
    else:
        for q, pr in KN.get(hira(w), []):
            v = nfv(pr); best = v if best is None or (v is not None and v < best) else best
    return best
# ---- 후보 모으기
rows = []
for w in W:
    rows.append({'kind': 'A', 'id': w['id'], 'w': w['w'], 'r': w['r'], 'bn': w.get('bn'), 'ord': w.get('ord'), 't': w['t']})
for o in OLD:
    if o['id'] in DROP_R: continue
    rows.append({'kind': 'R', 'id': o['id'], 'w': o['w'], 'r': o['r'], 'jlpt_old': RO.get(o['id'], {}).get('jlpt', '')})
for x in P4S:
    if x['src'] in DROP_N: continue
    rows.append({'kind': 'N', 'id': IDS[x['src']], 'src': x['src'], 'w': x['w'], 'r': x['r'], 'en': x['en'], 'lvsrc': int(x['lv'][1]), 'note': x.get('note', '')})
nid = max(IDS.values()) + 1; newids = {}
for x in P4ZF:
    if x['action'] == 'drop': continue
    z = P4Z[x['src']]
    if x['src'] not in IDS: IDS[x['src']] = nid; newids[x['src']] = nid; nid += 1
    rows.append({'kind': 'N', 'id': IDS[x['src']], 'src': x['src'], 'w': x['w'], 'r': x['r'], 'en': z['en'], 'lvsrc': int(z['lv'][1]), 'note': x.get('why', '') if x['action'] == 'change' else ''})
for r in rows:
    if r['kind'] == 'N': r['lv'], r['how'] = r['lvsrc'], 'src'
    else: r['lv'], r['how'] = level(r['w'], r['r'])
    r['wf'] = round(zf(clean_w(r['w']), 'ja'), 2)
    r['nf'] = nf_of(r['w'], r['r'])
both = [r['wf'] + math.log10((r['nf'] - 0.5) * 500) for r in rows if r['nf'] and r['wf'] > 0]
C = st.median(both)
for r in rows:
    nz = C - math.log10((r['nf'] - 0.5) * 500) if r['nf'] else min(r['wf'], C - math.log10(30000))
    r['nz'] = round(nz, 2)
    r['imp'] = round((r['wf'] + nz) / 2 - (0.3 if '〜' in r['w'] or '～' in r['w'] else 0), 3)
print('C =', round(C, 2), '· rows', len(rows), '· 새 id', len(newids), '(', min(newids.values(), default=0), '~', max(newids.values(), default=0), ')')
# 복원 카드: 예전 분류와 비교
ag = collections.Counter((r['jlpt_old'], r['lv']) for r in rows if r['kind'] == 'R')
print('복원 예전 jlpt vs 지금:', sorted(ag.items(), key=lambda x: -x[1])[:14])
# ---- 칸 만들기: 기본(bn) 카드는 N3·N2 칸에 넣지 않음
basic_ids = {r['id'] for r in rows if r['kind'] == 'A' and r['bn']}
sec = {3: [], 2: []}
seen = set()
for r in sorted(rows, key=lambda r: (-r['imp'], r['id'])):
    if r['lv'] not in (3, 2) or r['id'] in basic_ids: continue
    k = (clean_w(r['w']), clean_r(r['r']))
    if k in seen: r['dup'] = 1; continue
    seen.add(k); sec[r['lv']].append(r)
for L in (3, 2):
    for i, r in enumerate(sec[L]): r['jn'] = i + 1
    S = sec[L]; ck = lambda a, b: collections.Counter(r['kind'] for r in S[a:b])
    print(f'N{L} 전체 {len(S)} | 1~500 {dict(ck(0,500))} | 501~1000 {dict(ck(500,1000))} | 1001~ {dict(ck(1000,len(S)))}')
    print('  앞 40:', ' '.join(r['w'] for r in S[:40]))
    print('  480~500:', ' '.join(r['w'] for r in S[480:500]))
    print('  980~1000:', ' '.join(r['w'] for r in S[980:1000]))
    print('  끝 20:', ' '.join(r['w'] for r in S[-20:]))
# ---- 기본 501~ 재배열
B = sorted([r for r in rows if r['kind'] == 'A' and r['bn']], key=lambda r: r['bn'])
head, tail = B[:500], B[500:]
lvb = lambda r: 0.3 if r['lv'] == 5 else 0
tail2 = sorted(tail, key=lambda r: (-(r['imp'] + lvb(r)), r['bn']))
print('기본 501~ 새 순서 앞 40:', ' '.join(r['w'] for r in tail2[:40]))
print('기본 새 순서 끝 25:', ' '.join(r['w'] for r in tail2[-25:]))
print('새 501~1000 중 지금 886~ 출신', sum(r['bn'] > 885 for r in tail2[:500]))
json.dump({'C': C, 'n3': [{k: r[k] for k in ('kind', 'id', 'w', 'r', 'jn', 'imp', 'wf', 'nz', 'lv') } | ({'src': r['src'], 'en': r['en'], 'note': r['note']} if r['kind'] == 'N' else {}) for r in sec[3]],
           'n2': [{k: r[k] for k in ('kind', 'id', 'w', 'r', 'jn', 'imp', 'wf', 'nz', 'lv')} | ({'src': r['src'], 'en': r['en'], 'note': r['note']} if r['kind'] == 'N' else {}) for r in sec[2]],
           'basic_tail': [{'id': r['id'], 'w': r['w'], 'old_bn': r['bn'], 'new_bn': 501 + i, 'imp': r['imp'], 'lv': r['lv']} for i, r in enumerate(tail2)]},
          open(OUT + '/lv_order.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(rows, open(OUT + '/lv_rows.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(IDS, open(OUT + '/p4_ids_all.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
