"""한자 소리 두 번째 받아쓰기(ReazonSpeech) 전수 — 'これは X です' 사이에 넣어 X 부분 읽기 비교"""
import json, re, sys
from reazon import in_ctx, kana_of
from kana import kata2hira
R = '/home/claude/bjt-words'
J = json.load(open(R + '/tools/kanji_voice_jobs.json', encoding='utf-8'))
cards = {c['c']: c for c in json.load(open('/home/claude/work/kz/kz_cards.json', encoding='utf-8'))}
def h(t): return kata2hira(t)
def nl(s):   # 장음 정규화: ー → 앞 모음, おう/えい 같게
    s = h(s); out = ''
    V = {'a': 'あかさたなはまやらわがざだばぱゃ', 'i': 'いきしちにひみりぎじぢびぴ', 'u': 'うくすつぬふむゆるぐずづぶぷゅ', 'e': 'えけせてねへめれげぜでべぺ', 'o': 'おこそとのほもよろをごぞどぼぽょ'}
    def vow(c):
        for v, cs in V.items():
            if c in cs: return v
        return None
    for c in s:
        if c == 'ー' and out:
            v = vow(out[-1]); c = {'a': 'あ', 'i': 'い', 'u': 'う', 'e': 'い', 'o': 'う'}.get(v, '')
        out += c
    return out.replace('おお', 'おう')
def readings(c):
    k = cards.get(c); out = set()
    if not k: return out
    for r in k['on'] + k['kun']:
        r2 = r.replace('(', '').replace(')', ''); out.add(r2); out.add(r.split('(')[0])
    return out
rd = {j['key']: (j['t'].strip('「」『』'), j.get('v', '')) for j in J['kr']}
items = [(k, [h(rd[k][0])], 'k' if 'Keita' in rd[k][1] else 'n') for k in rd] + \
        [(k, [h(rd[p][0]) for p in ps], 'k' if all('Keita' in rd[p][1] for p in ps) else 'n') for k, ps in J['rep'].items()]
res = []; bad = 0
for n, (key, reads, car) in enumerate(items):
    t, kn = in_ctx(f'{R}/audio/{key}.mp3', car)
    mid = re.sub(r'^(これは|コレワ|これわ)', '', t); mid = re.sub(r'(です|デス)。?$', '', mid)
    exp = ''.join(reads); ok = False
    mk = nl(kana_of(mid)) if mid else ''
    if nl(mid) == nl(exp) or mk == nl(exp): ok = True
    elif len(reads) == 1 and len(mid) == 1 and reads[0] in readings(mid): ok = True
    elif len(reads) == 1 and mid and all(re.match(r'[一-鿿]', ch) for ch in mid[:1]) and any(reads[0].startswith(x) for x in readings(mid[0])) and nl(mid[1:]) == nl(reads[0][len(next(x for x in readings(mid[0]) if reads[0].startswith(x))):]): ok = True
    res.append({'key': key, 'exp': exp, 'text': t, 'mid': mid, 'mk': mk, 'ok': ok})
    if not ok: bad += 1
    if n % 300 == 0: print(n, len(items), flush=True)
json.dump(res, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('done', len(res), 'not ok', bad)
