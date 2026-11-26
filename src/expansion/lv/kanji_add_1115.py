#!/usr/bin/env python3
"""N3·N2 1,000번 이후 새 한자(11/15): kanji_lv3_raw.json(182자)에서 가나 표제로 바꿀 말의 한자 4자(汲 綴 掴 溜 — 상용 밖, 덱·gloss_dict가 이미 가나)를 빼고
→ n3p3/kanji/kanji_lv3.json (읽기 거르기 전) · kanji_mn/kzo_v2.json 맨 뒤에 새 묶음 'N3·N2 1,001~'(신문 빈도 → 단어 수 순)
  BJT 묶음 뒤에 붙이는 이유: 앞에 끼우면 BJT 한자 장의 위치(장 키)가 바뀌어 기록이 새로 시작됨
usage: python3 kanji_add_1115.py  (kzo_v2.json은 kzo_v2_pre1115.json으로 한 번만 백업)"""
import json, os, shutil, sys
E = '/home/claude/work/expansion'
sys.path.insert(0, E + '/tools')
from cardlib import kj_of
DROP = set('汲綴掴溜儲')   # 11/26: 儲도 뺌 — 1206·1207을 가나 표제(もうかる·もうける)로 바꿔 쓰는 단어가 없음(lv/n2p3/fix_kanji_n2p3.py가 이미 앱·kzo_v2에서 뺌)
raw = json.load(open(E + '/lv/kanji_lv3_raw.json', encoding='utf-8'))
K = {c: dict(e) for c, e in raw.items() if c not in DROP}
# 湧: 勇=힘차게는 한 학설뿐(검수 rvn3r) — 소리 부분으로만
K['湧']['s'] = '氵(물) + 勇(용, 소리) (涌의 이체자)'
K['湧']['x'] = '물(氵)이 솟아 나옴, 勇(용)은 소리 → 솟다, 생겨나다(湧く)'
D = json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8'))
assert not (set(K) & set(D['kanji'])), '이미 앱에 있는 한자'
L = json.load(open(E + '/lv/lv_order.json', encoding='utf-8'))
uses = {c: 0 for c in K}
for sec in ('n3', 'n2'):
    for x in L[sec]:
        if x.get('x') or x['jn'] <= 1000: continue
        for c in dict.fromkeys(kj_of(x['w'])):
            if c in uses: uses[c] += 1
assert all(uses.values()), [c for c, n in uses.items() if not n]
KD = json.load(open('/home/claude/kzdata/dl/kanji.json', encoding='utf-8'))
new = sorted(K, key=lambda c: ((KD.get(c) or {}).get('freq') or 9999, -uses[c], c))
json.dump(K, open(E + '/lv/n3p3/kanji/kanji_lv3.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
ZP = '/home/claude/work/kanji_mn/kzo_v2.json'; BK = '/home/claude/work/kanji_mn/kzo_v2_pre1115.json'
if not os.path.exists(BK): shutil.copy(ZP, BK)
Z = json.load(open(BK, encoding='utf-8'))
assert not (set(new) & set(Z['order']))
Z['order'] = Z['order'] + new
Z['groups'] = Z['groups'] + [['N3·N2 1,001~', len(new)]]
Z['note'] = Z['note'] + ' · 11/15: N3·N2 1,000번 이후 새 한자 %d자를 맨 뒤 묶음으로(BJT 장 키 그대로)' % len(new)
json.dump(Z, open(ZP, 'w', encoding='utf-8'), ensure_ascii=False)
print('새 한자', len(new), '· kzo', len(Z['order']), Z['groups'])
print('앞 20:', ''.join(new[:20]))
