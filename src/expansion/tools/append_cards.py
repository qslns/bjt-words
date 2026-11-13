#!/usr/bin/env python3
"""새 카드를 data_app.json 뒤에 붙이기 (11/13, 확장 P2~ · HANDOFF 5·7절)
쓰기: python3 append_cards.py --data IN.json --out OUT.json --order ORDER.json --cards A.jsonl [B.jsonl …] [--kanji K.json …] [--tt TT.json]
  ORDER.json  어디에 붙일지: [{"id":…, "bn":…}](기본) 또는 [{"id":…, "ord":…}](본편). basic_final.json 그대로 써도 됨
  --kanji     새 한자 항목 {"한자": {h,b,bn,s,x,on,kun,n}} (u는 이 도구가 다시 계산)
  --tt        예문 음성 글 고친 것 {"id-번호": "글"} (기본은 루비 뺀 글)
하는 일: hw·kj·예문 t 만들기, pr 표제어 → id, bn/ord 붙이기, 한자 u 전부 다시 계산(본편 ord 순 → 기본만 bn 순),
         기존 단어는 바이트까지 그대로인지 확인, 기존 한자는 u만 바뀌는지 확인. 카드 없이 돌리면 입력과 바이트까지 같아야 함.
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cardlib import make_hw, kj_of, strip_ruby, is_kanji

def dump(o): return json.dumps(o, ensure_ascii=False, separators=(',', ':'))

def compute_u(words, kanji):
    main = sorted([w for w in words if w.get('ord') is not None], key=lambda w: w['ord'])
    basic = sorted([w for w in words if w.get('ord') is None and w.get('bn') is not None], key=lambda w: w['bn'])
    out = {c: [] for c in kanji}
    for w in main + basic:
        for c in dict.fromkeys(w['kj']):
            if c in out: out[c].append(w['id'])
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default='/home/claude/work/build/data_app.json'); ap.add_argument('--out', required=True)
    ap.add_argument('--order'); ap.add_argument('--cards', nargs='*', default=[]); ap.add_argument('--kanji', nargs='*', default=[]); ap.add_argument('--tt')
    a = ap.parse_args()
    raw = open(a.data, encoding='utf-8').read()
    D = json.loads(raw)
    W, K = D['words'], D['kanji']
    before_w = [dump(w) for w in W]
    before_k = {c: dump({k: v for k, v in e.items() if k != 'u'}) for c, e in K.items()}
    # 0) 지금 데이터에서 u 재현 확인
    u0 = compute_u(W, K)
    badu = [c for c in K if u0[c] != K[c].get('u', [])]
    if badu: sys.exit('u 재현 안 됨: ' + ''.join(badu[:20]))
    ids = {w['id'] for w in W}
    heads = {w['w']: w['id'] for w in W}
    order = {}
    if a.order:
        for x in json.load(open(a.order, encoding='utf-8')):
            order[x['id']] = x
    cards = []
    for f in a.cards:
        for line in open(f, encoding='utf-8'):
            line = line.strip()
            if line: cards.append(json.loads(line))
    tt = json.load(open(a.tt, encoding='utf-8')) if a.tt else {}
    errs = []
    for c in cards:
        if c['id'] in ids: errs.append('id 이미 있음 %s' % c['id'])
        if c['id'] not in order: errs.append('순서표에 없는 id %s' % c['id'])
        if c['w'] in heads: errs.append('표제 이미 있음 %s %s' % (c['id'], c['w']))
        ids.add(c['id']); heads[c['w']] = c['id']
    if errs: sys.exit('\n'.join(errs[:30]))
    # 새 한자
    newk = {}
    for f in a.kanji:
        for ch, e in json.load(open(f, encoding='utf-8')).items():
            if ch in K: continue
            newk[ch] = e
    # 카드 → 단어
    used_bn = {w['bn'] for w in W if w.get('bn') is not None}; used_ord = {w['ord'] for w in W if w.get('ord') is not None}
    add = []
    for c in sorted(cards, key=lambda c: (order[c['id']].get('ord', 1e9), order[c['id']].get('bn', 1e9))):
        o = order[c['id']]
        hw = make_hw(c['w'], c['r'], c['kr'])
        if hw is None: errs.append('hw를 못 만듦 %s %s' % (c['id'], c['w'])); continue
        pr = []
        for x in c.get('pr', []):
            if isinstance(x, int): pr.append(x); continue
            if x.startswith('No.') and x[3:].isdigit():
                n = int(x[3:]); hit = [w['id'] for w in W if w.get('ord') == n - 1]
            elif x.startswith('B') and x[1:].isdigit():
                n = int(x[1:]); hit = [w['id'] for w in W if w.get('bn') == n]
            else: hit = [heads[x]] if x in heads else []
            if hit: pr.append(hit[0])
            else: print('경고: pr 못 찾음 %s %s → 뺌' % (c['id'], x))
        es = []
        for n, e in enumerate(c['e']):
            t = tt.get('%s-%d' % (c['id'], n)) or strip_ruby(e['j'])
            es.append({'s': e['s'], 'j': e['j'], 'k': e['k'], 't': t, 'g': e['g']})
        w = {'id': c['id'], 'w': c['w'], 'r': c['r'], 'm': c['m'], 't': c['t'], 'c': c['c'], 'p': c['p'], 'y': c['y'], 'o': c['o'],
             'hw': hw, 'ko': c['ko'], 'kj': kj_of(c['w']), 'kr': c['kr'], 'e': es}
        if 'ord' in o:
            if o['ord'] in used_ord: errs.append('ord 겹침 %s' % o['ord'])
            used_ord.add(o['ord'])
            w['pr'] = pr; w['ord'] = o['ord']; w['st'] = c['st']
            if o.get('bn') is not None: w['bn'] = o['bn']; used_bn.add(o['bn'])
        else:
            if o['bn'] in used_bn: errs.append('bn 겹침 %s' % o['bn'])
            used_bn.add(o['bn'])
            w['pr'] = pr; w['st'] = c['st']; w['bn'] = o['bn']
        if c.get('tw'): w['tw'] = c['tw']
        miss = [ch for ch in w['kj'] if ch not in K and ch not in newk]
        if miss: print('경고: 한자 항목 없음 %s %s: %s' % (c['id'], c['w'], ''.join(miss)))
        add.append(w)
    if errs: sys.exit('\n'.join(errs[:30]))
    # 이어지는지(빈 번호 없음)
    bns = sorted(w['bn'] for w in W + add if w.get('bn') is not None)
    ords = sorted(w['ord'] for w in W + add if w.get('ord') is not None)
    if bns != list(range(1, len(bns) + 1)): sys.exit('bn이 1부터 빈틈없이 이어지지 않음')
    if ords != list(range(len(ords))): sys.exit('ord가 0부터 빈틈없이 이어지지 않음')
    W2 = W + add
    K2 = dict(K)
    for ch, e in newk.items():
        K2[ch] = {k: e[k] for k in ('h', 'b', 'bn', 's', 'x', 'on', 'kun') if k in e}
        K2[ch]['u'] = []; K2[ch]['n'] = e.get('n', 0)
    u = compute_u(W2, K2)
    for ch in K2:
        e = K2[ch]
        K2[ch] = {k: (u[ch] if k == 'u' else e[k]) for k in ('h', 'b', 'bn', 's', 'x', 'on', 'kun', 'u', 'n') if k in e or k == 'u'}
    # 기존 것 그대로인지
    for i, s in enumerate(before_w):
        if dump(W2[i]) != s: sys.exit('기존 단어가 바뀜: %s' % W2[i]['id'])
    for ch, s in before_k.items():
        if dump({k: v for k, v in K2[ch].items() if k != 'u'}) != s: sys.exit('기존 한자 항목이 바뀜(u 말고): ' + ch)
    out = dump({'words': W2, 'kanji': K2, 'v': D['v']})
    if not cards and not newk and out != raw: sys.exit('카드 없이 돌렸는데 입력과 다름')
    open(a.out, 'w', encoding='utf-8').write(out)
    chu = sum(1 for ch in K if K2[ch]['u'] != K[ch]['u'])
    print('붙임 %d · 새 한자 %d · u 바뀐 한자 %d · 단어 %d → %d · 크기 %d → %d' % (len(add), len(newk), chu, len(W), len(W2), len(raw.encode()), len(out.encode())))

if __name__ == '__main__':
    main()
