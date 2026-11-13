#!/usr/bin/env python3
"""N3·N2 칸 작업 시트(11/13): lv_order.json에서 순위 구간 → 복원 손보기 묶음 + 새로 쓰기 묶음
4부(p34/cards4)에서 이미 손본 카드는 빼고(검수만), 앱에 있는 카드(A)도 뺌.
usage: python3 make_lv_sheets.py SEC FROM TO PREFIX [R묶음 47] [N묶음 35]   예: n3 1 500 n3a"""
import json, sys, re, os, glob, collections
sys.path.insert(0, '/home/claude/work/expansion/tools')
from cardlib import kj_of, hira
E = '/home/claude/work/expansion'
sec, a, b, pre = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
RS = int(sys.argv[5]) if len(sys.argv) > 5 else 47; NS = int(sys.argv[6]) if len(sys.argv) > 6 else 35
L = json.load(open(E + '/lv/lv_order.json', encoding='utf-8'))
d = json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8')); W, K = d['words'], d['kanji']
OK = json.load(open(E + '/old_kanji_extra.json', encoding='utf-8'))
NK = {}
for f in ('p2/kanji_new_p2.json', 'p34/kanji_new_p34.json'):
    NK.update(json.load(open(E + '/' + f, encoding='utf-8')))
HX = json.load(open(E + '/lv/kanji_h_lv.json', encoding='utf-8')) if os.path.exists(E + '/lv/kanji_h_lv.json') else {}
if os.path.exists(E + '/lv/kanji_h_tmp.json'):  # 11/13 23시: lvk1 결과 전 임시 훈음(시트용, 합칠 때는 lvk1 값)
    for k, v in json.load(open(E + '/lv/kanji_h_tmp.json', encoding='utf-8')).items(): HX.setdefault(k, v)
OLD = {w['id']: w for w in json.load(open(E + '/old_words_2312.json', encoding='utf-8'))}
KC = {x['c'] for x in json.load(open('/home/claude/work/kanji_mn/kanji_src.json', encoding='utf-8'))}
done4 = set()
for f in glob.glob(E + '/p34/cards4/*.jsonl'):
    for l in open(f, encoding='utf-8'):
        if l.strip(): done4.add(json.loads(l)['id'])
headw = {w['id']: w['w'] for w in W}; headw.update({i: w['w'] for i, w in OLD.items()})
byk = collections.defaultdict(list)
for w in W:
    for c in dict.fromkeys(w['kj']): byk[c].append(w['w'] + '=' + w['m'][:14])
nr = lambda r: re.sub(r'[～〜()（）\s]', '', hira(r))
byr = collections.defaultdict(list)
for w in W: byr[nr(w['r'])].append(w['w'] + '(' + w['m'][:12] + ')')
for w in OLD.values(): byr[nr(w['r'])].append(w['w'] + '(복원 ' + w['m'][:10] + ')')
for s2 in ('n3', 'n2'):
    for x in L[s2]:
        if x['kind'] == 'N': byr[nr(x['r'])].append(x['w'] + '(새 ' + s2.upper() + ')')
def kinfo(w):
    out = []
    for c in kj_of(w):
        e = K.get(c) or OK.get(c) or NK.get(c)
        h = e['h'] if e else HX.get(c, '?')
        out.append({'c': c, 'h': h, 'on': (e or {}).get('on', []), 'kun': (e or {}).get('kun', []), 'card': c in KC, 'deck_words': byk.get(c, [])[:6]})
    return out
R, N, skip4 = [], [], 0
for x in L[sec][a - 1:b]:
    if x['kind'] == 'A': continue
    if x['id'] in done4: skip4 += 1; continue
    homo = [h for h in byr[nr(x['r'])] if not h.startswith(x['w'] + '(')][:6]
    no = sec.upper() + ' No.' + str(x['jn'])
    if x['kind'] == 'R':
        o = OLD[x['id']]
        card = {'id': o['id'], 'w': o['w'], 'r': o['r'], 'm': o['m'], 't': o['t'], 'c': o['c'], 'ko': o['ko'], 'kr': o['kr'], 'p': o['p'], 'y': o['y'], 'o': o['o'], 'st': o['st'],
                'e': [{'s': e['s'], 'j': e['j'], 'k': e['k'], 'g': []} for e in o['e']], 'pr': [headw[i] for i in o.get('pr', []) if i in headw]}
        R.append({'no': no, 'jn': x['jn'], 'old_card': card, 'kanji': kinfo(o['w']), 'homophones': homo})
    else:
        N.append({'id': x['id'], 'jn': x['jn'], 'no': no, 'w': x['w'], 'r': x['r'], 'en': x['en'], 'lv': 'N' + str(x['lv']), 'note': x.get('note', ''), 'kanji': kinfo(x['w']), 'homophones': homo})
miss = sorted({k['c'] for s in R for k in s['kanji'] if k['h'] == '?'} | {k['c'] for s in N for k in s['kanji'] if k['h'] == '?'})
if miss: sys.exit('훈음 없는 한자: ' + ''.join(miss))
base = '/home/claude/agents'; made = []
for kind, items, size in (('r', R, RS), ('n', N, NS)):
    nb = (len(items) + size - 1) // size
    for i in range(nb):
        ch = items[i * size:(i + 1) * size]
        name = '%s%s%02d' % (pre, kind, i + 1); dd = '%s/%s' % (base, name)
        if os.path.exists(dd + '/sheet.json'): sys.exit('이미 있음: ' + name)
        os.makedirs(dd, exist_ok=True)
        json.dump(ch, open(dd + '/sheet.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        if kind == 'r': json.dump([c['old_card'] for c in ch], open(dd + '/old_cards.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        made.append((name, len(ch)))
print(sec, a, b, '· 복원', len(R), '· 새', len(N), '· 4부에서 손봄(뺌)', skip4, '·', made)
