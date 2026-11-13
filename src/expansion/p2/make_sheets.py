# P2-3 작업 시트: basic_final.json → 묶음 5개(시트마다 약 90장) → /home/claude/agents/p2w{n}/sheet.json
import json, sys, re, os, collections
sys.path.insert(0, '/home/claude/work/expansion/tools')
from cardlib import kj_of, hira
E = '/home/claude/work/expansion'
bf = json.load(open(E + '/basic_final.json', encoding='utf-8'))
d = json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8')); W, K = d['words'], d['kanji']
OK = json.load(open(E + '/old_kanji_extra.json', encoding='utf-8'))
NK = json.load(open(E + '/p2/kanji_new_p2.json', encoding='utf-8'))
old = json.load(open(E + '/old_words_2312.json', encoding='utf-8'))
KC = {x['c'] for x in json.load(open('/home/claude/work/kanji_mn/kanji_src.json', encoding='utf-8'))}
byk = collections.defaultdict(list)
for w in W:
    for c in dict.fromkeys(w['kj']): byk[c].append(w)
nr = lambda r: re.sub(r'[～〜()（）\s]', '', hira(r))
byr = collections.defaultdict(list)
for w in W: byr[nr(w['r'])].append(w['w'] + '(' + w['m'][:12] + ')')
for x in bf: byr[nr(x['r'])].append(x['w'] + '(새 기본)')
sheets = []
for x in bf:
    ks = []
    for c in kj_of(x['w']):
        src = 'app' if c in K else 'old' if c in OK else 'new'
        e = K.get(c) or OK.get(c) or NK.get(c)
        ks.append({'c': c, 'h': e['h'], 'on': e.get('on', []), 'kun': e.get('kun', []), 'card': c in KC, 'src': src,
                   'deck_words': [w['w'] + '=' + w['m'][:14] for w in sorted(byk.get(c, []), key=lambda w: (w.get('ord') is None, w.get('ord') or 0, w.get('bn') or 0))[:6]]})
    homo = [h for h in byr[nr(x['r'])] if not h.startswith(x['w'] + '(')]
    sheets.append({'id': x['id'], 'bn': x['bn'], 'w': x['w'], 'r': x['r'], 'en': x['en'], 'lv': x['lv'], 'note': x['note'], 'kanji': ks, 'homophones': homo[:6]})
cuts = [(886 + 45 * i, min(1331, 886 + 45 * i + 44)) for i in range(10)]
for n, (a, b) in enumerate(cuts, 1):
    part = [s for s in sheets if a <= s['bn'] <= b]
    os.makedirs('/home/claude/agents/p2w%d' % n, exist_ok=True)
    json.dump(part, open('/home/claude/agents/p2w%d/sheet.json' % n, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(n, a, b, len(part), ' '.join(s['w'] for s in part[:12]), '…')
