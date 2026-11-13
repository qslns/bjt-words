#!/usr/bin/env python3
"""앱에 이미 있는 카드 몇 칸 고치기(11/14) — 음성과 상관없는 칸(p·pr·m·y·st·g·k)만
usage: python3 app_fix.py DATA_IN.json DATA_OUT.json FIXES.json
FIXES.json: [{"id": 10020, "f": "p", "old": 지금 값, "new": 새 값}] — old가 지금 값과 다르면 멈춤. gN·kN은 예문 N번의 g·k"""
import sys, json, re
D = json.load(open(sys.argv[1], encoding='utf-8')); W = {w['id']: w for w in D['words']}
F = json.load(open(sys.argv[3], encoding='utf-8'))
for x in F:
    w = W[x['id']]; f = x['f']
    m = re.fullmatch(r'([gk])(\d)', f)
    if m: cur = w['e'][int(m.group(2))][m.group(1)]
    elif f in ('p', 'pr', 'm', 'y', 'st'): cur = w.get(f)
    else: sys.exit('이 칸은 못 고침: %s' % f)
    if cur != x['old']: sys.exit('지금 값이 다름 %s %s: %r' % (x['id'], f, cur))
    if m: w['e'][int(m.group(2))][m.group(1)] = x['new']
    else: w[f] = x['new']
    print('고침', x['id'], w['w'], f)
open(sys.argv[2], 'w', encoding='utf-8').write(json.dumps(D, ensure_ascii=False, separators=(',', ':')))
