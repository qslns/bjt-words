# 새 기본 카드의 hw(표제어 루비)·kj·kr(한자별 읽기)·ko(한국 한자음) 만들기 + 새 한자 목록
import json, re, sys, collections
sys.path.insert(0, '/home/claude/work/pipeline')
from jamdict import Jamdict
jam = Jamdict()
W = '/home/claude/work'
FUR = sys.argv[1]
L = json.load(open(f'{W}/basic/list.json', encoding='utf-8'))
D = json.load(open(f'{W}/build/data_final.json', encoding='utf-8'))
K = D['kanji']
def k2h(s): return ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in s or '')
def isk(c): return '一' <= c <= '鿿' or c in '々〆ヶ'
need = {(o['w'].replace('〜', ''), o['r']) for o in L if 'share' not in o}
furi = {}
for e in json.load(open(FUR, encoding='utf-8-sig')):
    k = (e['text'], e['reading'])
    if k in need: furi[k] = e['furigana']
def kd_on_kun(c):
    ch = jam.lookup(c).chars
    if not ch or not ch[0].rm_groups: return [], [], []
    rg = ch[0].rm_groups[0]
    on = [k2h(r.value) for r in rg.readings if r.r_type == 'ja_on']
    kun = [r.value.replace('-', '') for r in rg.readings if r.r_type == 'ja_kun']
    ko = [r.value for r in rg.readings if r.r_type == 'korean_h']
    return on, kun, ko
VOICE = dict(zip('かきくけこさしすせそたちつてとはひふへほ', 'がぎぐげござじずぜぞだぢづでどばびぶべぼ'))
def variants(x):
    out = {x}
    if x and x[0] in VOICE: out.add(VOICE[x[0]] + x[1:])
    if x and x[0] in 'はひふへほ': out.add(dict(zip('はひふへほ', 'ぱぴぷぺぽ'))[x[0]] + x[1:])
    for y in list(out):
        if len(y) > 1 and y[-1] in 'つちくき': out.add(y[:-1] + 'っ')
    return out
def cand_readings(c):
    on, kun, _ = kd_on_kun(c)
    rs = set()
    for o in on: rs |= variants(o)
    for k in kun:
        stem = k.split('.')[0]
        rs |= variants(stem)
        if '.' in k: rs |= variants(k.replace('.', ''))
    return rs
def split_run(run, rd):
    """한자 연속(run)의 읽기를 한 글자씩 나누기 (KANJIDIC 읽기 조합 탐색)"""
    if len(run) == 1: return [(run, rd)]
    c = run[0]
    for r in sorted(cand_readings(c), key=len, reverse=True):
        if rd.startswith(r) and len(rd) > len(r):
            rest = split_run(run[1:], rd[len(r):])
            if rest: return [(c, r)] + rest
    return None
def align(head, rd):
    parts = re.findall(r'[一-鿿々〆ヶ]+|[^一-鿿々〆ヶ]+', head)
    pat = ''.join('(.+?)' if isk(p[0]) else '(' + re.escape(k2h(p)) + ')' for p in parts)
    m = re.fullmatch(pat, k2h(rd))
    if not m: return None
    return [(p, g if isk(p[0]) else '') for p, g in zip(parts, m.groups())]
out = {}; newk = collections.Counter(); prob = []
for o in L:
    if 'share' in o: continue
    head = o['w'].replace('〜', ''); rd = o['r']
    if not any(isk(c) for c in head):
        out[o['bn']] = {'hw': o['w'], 'kj': [], 'kr': [], 'ko': ''}; continue
    seg = align(head, rd)
    if not seg: prob.append(('align', o['w'], rd)); seg = [(head, rd)]
    pre = '〜' if o['w'].startswith('〜') else ''
    hw = pre + ''.join(f'[{t}|{r}]' if r else t for t, r in seg)
    kj = [c for c in head if isk(c)]
    kr = []
    f = furi.get((head, rd))
    if f:
        for x in f:
            if 'rt' in x and x['rt'] and any(isk(c) for c in x['ruby']):
                if len(x['ruby']) == 1: kr.append([x['ruby'], x['rt']])
                else: kr = None; break   # 숙자훈(통째 읽기)
    else:
        for t, r in seg:
            if not r: continue
            sp = split_run(t, r)
            if sp is None: kr = None; prob.append(('split', o['w'], rd, t, r)); break
            kr += [[a, b] for a, b in sp]
    if kr is None: kr = []
    ko = ''
    for c in kj:
        if c in K and K[c].get('h'): ko += K[c]['h'].split()[-1]
        else:
            _, _, kk = kd_on_kun(c); ko += (kk[0] if kk else '?')
    for c in kj:
        if c not in K: newk[c] += 1
    out[o['bn']] = {'hw': hw, 'kj': kj, 'kr': kr, 'ko': ko}
json.dump(out, open(f'{W}/basic/headinfo.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(sorted(newk), open(f'{W}/basic/newkanji.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('cards', len(out), '| new kanji', len(newk), ''.join(sorted(newk, key=lambda c: -newk[c])))
print('jukujikun (kr empty):', [L[b - 1]['w'] for b, v in out.items() if v['kj'] and not v['kr']])
for p in prob: print(' ', p)
