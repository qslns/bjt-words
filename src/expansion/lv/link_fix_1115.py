"""11/15 한자 연결 점검 고침(사용자 11/13·11/15: 연결이 덜 된 곳을 전체 데이터에서 찾아 고치기). 여러 번 돌려도 같은 결과.
usage: python3 link_fix_1115.py DATA_IN.json DATA_OUT.json CARDS_IN.json CARDS_OUT.json LOG.txt
점검 결과(11/15 데이터 4,243개 · 한자 1,434): 표제 한자(kj)·한자 단어 목록(u)은 전부 맞음(빠짐·넘침 0). 고친 것:
1) 헷갈리는 짝(pr): 처음 BJT 카드끼리는 늘 양쪽으로 이어져 있었는데(한쪽만 0), 기본·N3·N2 카드를 붙이면서 옛 카드는 안 건드려
   한쪽만 이어진 것이 생김(기본→기본 325 · N3·N2→기본 316 · N3·N2끼리 185 · 기본·N3·N2→BJT 514 등 1,341) → 반대쪽 끝에 덧붙임.
   (같은 표제 来る きたる↔くる, 〜別↔別, ある↔ある〜 도 여기서 이어짐)
2) 한자 읽기 짝(kr)이 빠진 표제: 〜商(しょう)·〜通(つう).
3) 단어에 쓰이는데 한자 읽기 목록에 없던 상용 읽기: 上 うわ(上着·上回る·上〜) · 度 タク(支度) · 財 サイ(財布) · 納 ナッ(納得) ·
   外 ゲ(外科) · 命 ミョウ(寿命) · 並 な(み)→なみ(並木 — 어간 な + 送り仮名 み로 잘못 적혀 있었음).
   付表·특수 읽기(お父さん とう·お母さん かあ·兄さん にい·姉さん ねえ·お腹 なか·日本 に·各々 おの)는 그대로.
   그림 카드(kz_cards)의 on/kun도 같이 고침(음독은 히라가나)."""
import json, sys
DI, DO, CI, CO, LOG = sys.argv[1:6]
D = json.load(open(DI, encoding='utf-8')); W = D['words']; K = D['kanji']
C = json.load(open(CI, encoding='utf-8')); CM = {c['c']: c for c in C}
by = {w['id']: w for w in W}
log = []
# 1) pr 양쪽
add = {}
for w in W:
    for p in w.get('pr') or []:
        b = by.get(p)
        if b is None or p == w['id']: continue
        if w['id'] not in (b.get('pr') or []): add.setdefault(p, []).append(w['id'])
n_pr = 0
for w in W:   # 단어 순서대로 돌며 덧붙임(결과가 늘 같게)
    xs = add.get(w['id'])
    if not xs: continue
    cur = list(w.get('pr') or [])
    for x in xs:
        if x not in cur: cur.append(x); n_pr += 1; log.append('pr\t%d %s\t+%d %s' % (w['id'], w['w'], x, by[x]['w']))
    w['pr'] = cur
# 2) kr
KR_FIX = {'〜商': [['商', 'しょう']], '〜通': [['通', 'つう']]}
n_kr = 0
for w in W:
    if w['w'] in KR_FIX and not w.get('kr'):
        w['kr'] = KR_FIX[w['w']]; n_kr += 1; log.append('kr\t%d %s\t%s' % (w['id'], w['w'], w['kr']))
# 3) 한자 읽기
hira = lambda s: ''.join(chr(ord(ch) - 0x60) if 'ァ' <= ch <= 'ヶ' else ch for ch in s)
ADD_ON = {'度': 'タク', '財': 'サイ', '納': 'ナッ', '外': 'ゲ', '命': 'ミョウ'}
ADD_KUN = {'上': 'うわ'}
REN_KUN = {'並': ('な(み)', 'なみ')}
n_rd = 0
for c, r in ADD_ON.items():
    if r not in K[c]['on']:
        K[c]['on'] = K[c]['on'] + [r]; n_rd += 1; log.append('on\t%s +%s' % (c, r))
    if c in CM and hira(r) not in CM[c]['on']: CM[c]['on'] = CM[c]['on'] + [hira(r)]
for c, r in ADD_KUN.items():
    if r not in K[c]['kun']:
        K[c]['kun'] = K[c]['kun'] + [r]; n_rd += 1; log.append('kun\t%s +%s' % (c, r))
    if c in CM and r not in CM[c]['kun']: CM[c]['kun'] = CM[c]['kun'] + [r]
for c, (a, b) in REN_KUN.items():
    if a in K[c]['kun']:
        K[c]['kun'] = [b if x == a else x for x in K[c]['kun']]; n_rd += 1; log.append('kun\t%s %s→%s' % (c, a, b))
    if c in CM and a in CM[c]['kun']: CM[c]['kun'] = [b if x == a else x for x in CM[c]['kun']]
# 카드와 앱 한자 자료가 같은지
for c, card in CM.items():
    assert card['on'] == [hira(x) for x in K[c]['on']] and card['kun'] == K[c]['kun'], c
json.dump(D, open(DO, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(C, open(CO, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
open(LOG, 'w', encoding='utf-8').write('\n'.join(log) + '\n')
print('pr 덧붙임', n_pr, '· kr', n_kr, '· 한자 읽기', n_rd)
