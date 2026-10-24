"""0부 기본 카드 만들기: data_final.json + 기본 카드(bn ≤ LIMIT) → build/data_app.json
usage: build_basic.py LIMIT"""
import json, re, sys, glob, os, collections
sys.path.insert(0, '/home/claude/work/basic'); sys.path.insert(0, '/home/claude/work/pipeline'); sys.path.insert(0, '/home/claude/work/final')
import gloss_b, gloss_fix
from kanji_check import RAD, AMBIG
from jamdict import Jamdict
jam = Jamdict()
LIMIT = int(sys.argv[1])
Wd = '/home/claude/work'
L = json.load(open(f'{Wd}/basic/list.json', encoding='utf-8'))
HI = json.load(open(f'{Wd}/basic/headinfo.json', encoding='utf-8'))
KEEP = json.load(open(f'{Wd}/basic/keep.json', encoding='utf-8'))
NEW = json.load(open(f'{Wd}/basic/new_proc.json', encoding='utf-8'))
D = json.load(open(f'{Wd}/build/data_final.json', encoding='utf-8'))
words, K = D['words'], D['kanji']
byid = {w['id']: w for w in words}
BASE = 9000
KO_FIX = {'壊れる': '괴', '医者': '의자', '計画': '계획', '楽しみ': '락', '楽しい': '락', '楽しむ': '락', '壊す': '괴', '〜台': '대', 'お茶': '차'}   # KANJIDIC 한국 한자음이 틀린 경우
def dueum(ko):   # 두음법칙: 한자 2자 이상 낱말의 첫 음 (래월→내월, 려행→여행, 녀성→여성)
    if not ko or not ('가' <= ko[0] <= '힣'): return ko
    n = ord(ko[0]) - 0xAC00; ini, med, fin = n // 588, (n % 588) // 28, n % 28
    if ini == 5: ini = 11 if med in (2, 6, 7, 12, 17, 20) else 2
    elif ini == 2 and med in (2, 6, 7, 12, 17, 20): ini = 11
    else: return ko
    return chr(0xAC00 + ini * 588 + med * 28 + fin) + ko[1:]
def plain(j): return re.sub(r'[{}]', '', re.sub(r'\[([^|\]]+)\|[^\]]*\]', r'\1', j))
prob = []
# 단어 음성: 한자 그대로 주면 음성 엔진이 다른 읽기를 고를 수 있는 표제어는 가나로 읽힘 (10/14 검수)
TW_B = {307: 'いちにち', 241: 'まいつき', 287: 'だいじ', 491: 'あく', 510: 'まいとし', 512: 'おおぜい', 725: 'ひるま', 738: 'まいあさ',
        740: 'じょうず', 752: 'へた', 802: 'まじめ', 872: 'このごろ', 791: 'よごれる', 768: 'おこる', 187: 'はいる'}
# ---- 카드 ----
recs = []; aumap = {}
for o in L:
    bn = o['bn']
    if bn > LIMIT: continue
    if 'share' in o:
        byid[o['share']]['bn'] = bn; continue
    hi = HI[str(bn)]; nid = BASE + bn
    es = []
    for p in KEEP.get(str(bn), []):
        src = byid[p['wid']]['e'][p['i']]
        if plain(src['j']) != plain(p['j']): prob.append(f'#{bn} pick text differs: {plain(src["j"])} / {plain(p["j"])}')
        old = {a: b for a, b in src.get('g', [])}
        g = [[a, old.get(a, b)] for a, b in gloss_b.gloss_sentence(p['j'])]
        aumap[f'{nid}-{len(es)}'] = [p['wid'], p['i']]
        es.append({'s': src['s'], 'j': p['j'], 'k': p['k'], 't': src['t'], 'g': g})
    for e in NEW.get(str(bn), []):
        es.append({'s': e['s'], 'j': e['j'], 'k': e['k'], 't': e['t'], 'g': gloss_b.gloss_sentence(e['j'])})
    if len(es) not in (2, 3): prob.append(f'#{bn} {o["w"]} sentences={len(es)}')
    for e in es:
        if e['j'].count('{') != 1: prob.append(f'#{bn} target mark: {e["j"]}')
    kj = [c for c in hi['kj'] if c != '々']
    ko = hi['ko']
    if '?' in ko and '々' in o['w']:   # 々 자리의 한국 한자음은 앞 글자를 되풀이
        ks = [c for c in o['w'] if '一' <= c <= '鿿' or c == '々']
        ko = ''.join((ko[i - 1] if (c == '々' and i > 0) else ko[i]) for i, c in enumerate(ks)) if len(ks) == len(ko) else ko.replace('?', '')
    ko = KO_FIX.get(o['w'], ko)
    if sum(1 for c in o['w'] if '一' <= c <= '鿿' or c == '々') >= 2: ko = dueum(ko)
    recs.append({'id': nid, 'w': o['w'], 'r': o['r'], 'm': o['m'], 't': 'K', 'c': o['c'], 'p': o.get('p', ''), 'y': '', 'o': '',
                 'hw': hi['hw'], 'ko': ko, 'kj': kj, 'kr': hi['kr'], 'e': es, 'pr': [], 'st': '', 'bn': bn})
    if bn in TW_B: recs[-1]['tw'] = TW_B[bn]
# 예문 번역 바로잡기 (본편에서 가져온 예문도 기본 카드 쪽 번역만 바꿈)
KF = {}
for ln in open(f'{Wd}/basic/kfix_b.tsv', encoding='utf-8'):
    if not ln.strip() or ln.startswith('#'): continue
    b_, i_, k_ = ln.rstrip('\n').split('\t'); KF[(int(b_), int(i_))] = k_
for r in recs:
    for i, e in enumerate(r['e']):
        if (r['bn'], i) in KF: e['k'] = KF.pop((r['bn'], i))
for k_ in KF: prob.append(f'kfix unused {k_}')
# 본편과 같은 칸 채우기: 이야기(st)·BJT 포인트(p)·바꿔 말하면(y)·어원(o)·헷갈리는 짝(pr) ← basic/x/ex_*.txt
import extras
EX = extras.load(words + recs, prob)
recbn = {r['bn'] for r in recs}
for r in recs:
    x = EX.get(r['bn'])
    if not x: prob.append(f"#{r['bn']} {r['w']} extras missing"); continue
    r['st'], r['y'], r['o'] = x['st'], x['y'], x['o']
    if x['p'] != '=': r['p'] = x['p']
    r['pr'] = list(dict.fromkeys(i for i in x['prids'] if i != r['id']))
    if not r['st'] or not r['p']: prob.append(f"#{r['bn']} {r['w']} empty st/p")
for bn in EX:
    if bn <= LIMIT and bn not in recbn: prob.append(f'extras for non-basic-only card #{bn}')
n_g, _ = gloss_fix.apply(recs)
# 기본 예문 전용 풀이 바로잡기 (문장 패턴, 지금 표제, 지금 뜻(None=아무거나), 새 표제(None=삭제), 새 뜻)
RB = []
for ln in open(f'{Wd}/basic/gfix_b.tsv', encoding='utf-8'):
    if not ln.strip() or ln.startswith('#'): continue
    f = ln.rstrip('\n').split('\t') + ['', '', '', '', '']
    RB.append((f[0], f[1], f[2] or None, f[3] or None, f[4]))
saveR = gloss_fix.R; gloss_fix.R = RB
n_gb, unused_b = gloss_fix.apply(recs)
gloss_fix.R = saveR
# 「〜すると」(する+と)를 접속사 すると(그러자)로 잘못 단 풀이 지우기
for e in (e for r in recs for e in r['e']):
    pl = plain(e['j'])
    if any(a == 'すると' for a, b in e['g']) and not re.search(r'(^|[。、」])すると', pl):
        e['g'] = [x for x in e['g'] if x[0] != 'すると']
for e in (e for r in recs for e in r['e']):
    for a, b in e['g']:
        if b.count('(') != b.count(')'): prob.append(f'gloss paren: {a} {b} | {plain(e["j"])}')
# ---- 한자 ----
def kd(c):
    r = jam.lookup(c).chars
    if not r: return {'rad': None, 'n': 0, 'ko': []}
    ch = r[0]; rg = ch.rm_groups[0] if ch.rm_groups else None
    return {'rad': int(ch.radicals[0].value) if ch.radicals else None, 'n': ch.stroke_count or 0,
            'ko': [x.value for x in rg.readings if x.r_type == 'korean_h'] if rg else []}
radadd = {}
for p in glob.glob(f'{Wd}/kanji_new/radicals_add*.tsv') + [f'{Wd}/basic/radicals_add_b.tsv']:
    if not os.path.exists(p): continue
    for ln in open(p, encoding='utf-8'):
        f = ln.rstrip('\n').split('\t')
        if len(f) >= 3 and f[1].strip().isdigit(): radadd[f[0].strip()] = (int(f[1]), f[2].strip())
def rad_name(form, num):
    if form in AMBIG: return AMBIG[form].get(num, '')
    if form in RAD: return RAD[form][1]
    if form in radadd: return radadd[form][1]
    return ''
ent = {}
for p in sorted(glob.glob(f'{Wd}/kanji_new/k*.txt')) + [f'{Wd}/basic/kanji_b.txt']:
    for ln in open(p, encoding='utf-8'):
        f = ln.rstrip('\n').split('|')
        if len(f) == 5: ent[f[0]] = f
DK = json.load(open(f'{Wd}/build/data.json', encoding='utf-8'))['kanji']
RA = json.load(open(f'{Wd}/basic/kread_auto.json', encoding='utf-8'))
for ln in open(f'{Wd}/basic/kread_man.tsv', encoding='utf-8'):
    if ln.startswith('#') or not ln.strip(): continue
    c, on, kun = (ln.rstrip('\n').split('\t') + ['', ''])[:3]
    RA[c] = {'on': [x for x in on.split('・') if x], 'kun': [x for x in kun.split('・') if x]}
newk = 0
for r in recs + [w for w in words if w.get('bn')]:
    for c in r['kj']:
        if c not in K:
            if c in ent:
                _, h, b, s, x = ent[c]; i = kd(c)
                K[c] = {'h': h, 'b': b, 'bn': rad_name(b, i['rad']), 's': s, 'x': x, 'on': RA.get(c, {}).get('on', []), 'kun': RA.get(c, {}).get('kun', []), 'u': [], 'n': i['n']}
            elif c in DK:
                d = dict(DK[c]); d['on'] = RA.get(c, {}).get('on', d.get('on', [])); d['kun'] = RA.get(c, {}).get('kun', d.get('kun', [])); d['u'] = []
                K[c] = d
            else:
                prob.append(f'NO KANJI ENTRY {c} ({r["w"]})'); continue
            newk += 1
            k = K[c]
            if not k['bn']: prob.append(f'radical name missing {c} {k["b"]}')
            eums = [p.strip().split()[-1] for p in k['h'].split('/') if p.strip()]
            ko = kd(c)['ko']
            if ko and not any(e in ko for e in eums): prob.append(f'eum mismatch {c} {k["h"]} kanjidic={ko}')
        if r['id'] not in K[c]['u']: K[c]['u'].append(r['id'])
words2 = words + recs
out = {'words': words2, 'kanji': K, 'v': D.get('v')}
json.dump(out, open(f'{Wd}/build/data_app.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(aumap, open(f'{Wd}/basic/audio_map.json', 'w', encoding='utf-8'))
print('basic new cards', len(recs), 'shared', sum(1 for w in words if w.get('bn')), 'new kanji', newk, 'gloss fixes', n_g, n_gb, 'unused basic rules', len(unused_b))
for u in unused_b: prob.append(f'unused basic gloss rule {u}')
for p in prob: print('PROB', p)
