#!/usr/bin/env python3
"""N2 3·4부 합친 뒤 한자 고침(11/26) — append_cards 다음, 그림 카드 k2c06·07 합치기 전에 돌림
① 儲: 1206 儲かる·1207 儲ける가 가나 표제(もうかる·もうける)가 되어 쓰는 단어가 없음 → 한자 칸(kzo_v2 순서·마지막 묶음)과 앱 자료에서 뺌
   (11/15 汲·綴·掴·溜를 넣기 전에 뺀 것과 같은 이유. kanji_add_1115.py를 다시 돌리면 그 assert가 걸리니 그 파일 머리에 적어 둠)
② N2 단어가 쓰는 常用 읽기인데 한자 카드에 없던 것 더함: 読 トウ(句読点) · 船 ふな(船便) · 献 コン(献立) · 下 お(ろす)(見下ろす) · 坊 ボッ(坊ちゃん) · 塞 ふさ(がる)(塞がる)
③ 획수: 2010년 常用 추가자 중 옛 KANJIDIC 획수가 그림(常用 자형, KanjiVG)과 다른 것 → 常用 획수로: 僅 13 · 謎 17 · 餅 15 · 賭 16 · 餌 15 · 遜 14 · 遡 14
   → 앱 자료 on/kun · 그림 카드 kz_cards on/kun(카드가 있는 것) · kz_imp(흘려보기로 뒤에 — fix1126과 같은 방식)
usage: python3 fix_kanji_n2p3.py DATA (제자리 고침, 처음 한 번 *_pre_n2p3fix 백업)"""
import json, sys, os, shutil, re
DP = sys.argv[1]
KC, KI, KZO = '/home/claude/work/kz/kz_cards.json', '/home/claude/work/kz/kz_imp.json', '/home/claude/work/kanji_mn/kzo_v2.json'
for p in (DP, KC, KI, KZO):
    b = re.sub(r'\.json$', '_pre_n2p3fix.json', p)
    if not os.path.exists(b): shutil.copy(p, b)
D = json.load(open(DP, encoding='utf-8')); K = D['kanji']
C = json.load(open(KC, encoding='utf-8')); I = json.load(open(KI, encoding='utf-8')); Z = json.load(open(KZO, encoding='utf-8'))
# ① 儲
users = [w['w'] for w in D['words'] if '儲' in w['w'] or any(ch == '儲' for ch, _ in (w.get('kr') or []))]
assert not users, users
assert '儲' in K and '儲' in Z['order'] and '儲' not in {c['c'] for c in C} and '儲' not in I
del K['儲']
Z['order'].remove('儲')
g = Z['groups'][-1]; assert g[0].startswith('N3·N2 1,001'), g[0]
if isinstance(g[1], list): g[1] = [c for c in g[1] if c != '儲']
elif isinstance(g[1], int): g[1] -= 1
else: g[1] = g[1].replace('儲', '')
# ② 읽기
CB = {c['c']: c for c in C}
hira = lambda s: ''.join(chr(ord(ch) - 0x60) if 'ァ' <= ch <= 'ヶ' else ch for ch in s)
ADD_ON = {'読': 'トウ', '献': 'コン', '坊': 'ボッ'}
ADD_KUN = {'船': 'ふな', '下': 'お(ろす)', '塞': 'ふさ(がる)'}
for ch, r in ADD_ON.items():
    if r not in K[ch]['on']: K[ch]['on'] = K[ch]['on'] + [r]
    if ch in CB and hira(r) not in CB[ch]['on']: CB[ch]['on'] = CB[ch]['on'] + [hira(r)]
    if ch in I and not any(x == hira(r) for x, _, _ in I[ch]['on']):
        I[ch]['on'] = I[ch]['on'] + [[hira(r), max(n for _, n, _ in I[ch]['on'] + I[ch]['kun']) + 1, 1]]
for ch, r in ADD_KUN.items():
    if r not in K[ch]['kun']: K[ch]['kun'] = K[ch]['kun'] + [r]
    if ch in CB and r not in CB[ch]['kun']: CB[ch]['kun'] = CB[ch]['kun'] + [r]
    if ch in I and not any(x == r for x, _, _ in I[ch]['kun']):
        I[ch]['kun'] = I[ch]['kun'] + [[r, max(n for _, n, _ in I[ch]['on'] + I[ch]['kun']) + 1, 1]]
for ch in list(ADD_ON) + list(ADD_KUN):
    print(ch, 'app', K[ch]['on'], K[ch]['kun'], '| card', (CB[ch]['on'], CB[ch]['kun']) if ch in CB else '-', '| imp', (I[ch]['on'], I[ch]['kun']) if ch in I else '-')
STROKES = {'僅': 13, '謎': 17, '餅': 15, '賭': 16, '餌': 15, '遜': 14, '遡': 14}
for ch, n in STROKES.items():
    print('획수', ch, K[ch].get('n'), '→', n); K[ch]['n'] = n
print('儲 뺌 · 한자 칸', len(Z['order']), '· 마지막 묶음', g[0])
json.dump(D, open(DP, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(C, open(KC, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(I, open(KI, 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(Z, open(KZO, 'w', encoding='utf-8'), ensure_ascii=False)
