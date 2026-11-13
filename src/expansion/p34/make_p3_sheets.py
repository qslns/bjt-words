# P3+P4 작업 시트(부마다): main_order.json에서 그 부(500개) → 복원 카드 묶음(옛 카드를 작성 꼴로) + 새 N3·N2 카드 묶음
# usage: python3 make_p3_sheets.py 4 [묶음 크기 46]
import json, sys, re, os, collections
sys.path.insert(0, '/home/claude/work/expansion/tools')
from cardlib import kj_of, hira
E = '/home/claude/work/expansion'
part = int(sys.argv[1]); size = int(sys.argv[2]) if len(sys.argv) > 2 else 46
KEEP = set(sys.argv[3].split(',')) if len(sys.argv) > 3 else set()   # 이미 작업 중인 묶음 폴더 이름: 덮어쓰지 않음(내용이 같은지만 확인)
order = json.load(open(E + '/p34/main_order.json', encoding='utf-8'))
lo, hi = 1500 + (part - 4) * 500, 1500 + (part - 4) * 500 + 499
sel = [x for x in order if lo <= x['ord'] <= hi]
d = json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8')); W, K = d['words'], d['kanji']
OK = json.load(open(E + '/old_kanji_extra.json', encoding='utf-8'))
NK = {}
for f in ('p2/kanji_new_p2.json', 'p34/kanji_new_p34.json'):
    if os.path.exists(E + '/' + f): NK.update(json.load(open(E + '/' + f, encoding='utf-8')))
OLD = {w['id']: w for w in json.load(open(E + '/old_words_2312.json', encoding='utf-8'))}
BF = json.load(open(E + '/basic_final.json', encoding='utf-8'))
KC = {x['c'] for x in json.load(open('/home/claude/work/kanji_mn/kanji_src.json', encoding='utf-8'))}
headw = {w['id']: w['w'] for w in W}; headw.update({i: w['w'] for i, w in OLD.items()})
byk = collections.defaultdict(list)
for w in W:
    for c in dict.fromkeys(w['kj']): byk[c].append(w['w'] + '=' + w['m'][:14])
nr = lambda r: re.sub(r'[～〜()（）\s]', '', hira(r))
byr = collections.defaultdict(list)
for w in W: byr[nr(w['r'])].append(w['w'] + '(' + w['m'][:12] + ')')
for w in OLD.values(): byr[nr(w['r'])].append(w['w'] + '(복원 ' + w['m'][:10] + ')')
for x in BF: byr[nr(x['r'])].append(x['w'] + '(새 기본)')
for x in order:
    if x['kind'] == 'N': byr[nr(x['r'])].append(x['w'] + '(새 N3·N2)')
def kinfo(w):
    out = []
    for c in kj_of(w):
        e = K.get(c) or OK.get(c) or NK.get(c)
        out.append({'c': c, 'h': e['h'] if e else '?', 'on': (e or {}).get('on', []), 'kun': (e or {}).get('kun', []), 'card': c in KC, 'deck_words': byk.get(c, [])[:6]})
    return out
R, N = [], []
for x in sel:
    homo = [h for h in byr[nr(x['r'])] if not h.startswith(x['w'] + '(')][:6]
    if x['kind'] == 'R':
        o = OLD[x['id']]
        card = {'id': o['id'], 'w': o['w'], 'r': o['r'], 'm': o['m'], 't': o['t'], 'c': o['c'], 'ko': o['ko'], 'kr': o['kr'], 'p': o['p'], 'y': o['y'], 'o': o['o'], 'st': o['st'],
                'e': [{'s': e['s'], 'j': e['j'], 'k': e['k'], 'g': []} for e in o['e']], 'pr': [headw[i] for i in o.get('pr', []) if i in headw]}
        R.append({'ord': x['ord'], 'no': x['ord'] + 1, 'old_card': card, 'kanji': kinfo(o['w']), 'homophones': homo})
    else:
        N.append({'id': x['id'], 'ord': x['ord'], 'no': x['ord'] + 1, 'w': x['w'], 'r': x['r'], 'en': x['en'], 'lv': x['lv'], 'note': x.get('note', ''), 'kanji': kinfo(x['w']), 'homophones': homo})
base = '/home/claude/agents'
nb = (len(R) + size - 1) // size
for b in range(nb):
    ch = R[b * size:(b + 1) * size]
    name = 'p%dr%02d' % (part, b + 1); dd = '%s/%s' % (base, name); os.makedirs(dd, exist_ok=True)
    if name in KEEP:
        cur = json.load(open(dd + '/sheet.json', encoding='utf-8'))
        if [c['old_card']['id'] for c in cur] != [c['old_card']['id'] for c in ch]: sys.exit('작업 중인 묶음 %s의 내용이 바뀜 — 멈춤' % name)
        print('keep', name); continue
    json.dump(ch, open(dd + '/sheet.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump([c['old_card'] for c in ch], open(dd + '/old_cards.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
dd = '%s/p%dn' % (base, part); os.makedirs(dd, exist_ok=True)
json.dump(N, open(dd + '/sheet.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('part', part, 'restore', len(R), 'in', nb, 'batches · new N3N2', len(N))
