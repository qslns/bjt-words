"""11/15 K2 N3·N2 한자 326자: 검수본 12묶음 → 검사 → 컴파일 → kz_cards 뒤에 덧붙임 + 읽기 중요도 다시 계산.
usage: python3 k2b_merge.py OUTDIR
- 검수본: k2b01~03 = rk2c, 04~06 = rk2d, 07~09 = rk2e, 10~12 = rk2f (/home/claude/agents/<검수자>/k2bNN.json)
- 옛 1,108장은 그대로(객체 비교), 새 326장은 한자 칸 순서(kzo_v2)대로 뒤에
- kz_imp: 전체 1,434장으로 다시 계산 → 옛 1,108자 항목이 지금 kz_imp.json과 같은지 확인(단어 자료가 그대로이면 같아야 함)
결과: OUTDIR/kz_cards_k2b.json · kz_imp_k2b.json · new_cards.json"""
import json, sys, os, subprocess
KZ = '/home/claude/work/kz'; AG = '/home/claude/agents'
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
REV = {1: 'rk2c', 2: 'rk2c', 3: 'rk2c', 4: 'rk2d', 5: 'rk2d', 6: 'rk2d', 7: 'rk2e', 8: 'rk2e', 9: 'rk2e', 10: 'rk2f', 11: 'rk2f', 12: 'rk2f'}
B = json.load(open(AG + '/common/k2_batches.json', encoding='utf-8'))
files = []
for n in range(1, 13):
    name = 'k2b%02d' % n; f = '%s/%s/%s.json' % (AG, name if os.environ.get('K2B_SRC') == 'writers' else REV[n], name)   # K2B_SRC=writers: 검수 전 작성본으로 미리 돌려 보기
    assert os.path.exists(f), f
    cs = json.load(open(f, encoding='utf-8'))
    got = ''.join(c['c'] for c in cs)
    assert got == B[name], (name, got, B[name])
    files.append(f)
r = subprocess.run(['python3', KZ + '/kzc.py', 'validate'] + files, cwd=KZ, capture_output=True, text=True)
print(r.stdout.strip().splitlines()[-1])
warn = [l for l in r.stdout.splitlines() if l.strip().startswith('주의')]
for l in warn: print(l)
assert r.returncode == 0, r.stdout[-3000:]
r = subprocess.run(['python3', KZ + '/kzc.py', 'compile', '-o', OUT + '/new_cards.json'] + files, cwd=KZ, capture_output=True, text=True)
print(r.stdout.strip()); assert r.returncode == 0, r.stderr[-2000:]
new = json.load(open(OUT + '/new_cards.json', encoding='utf-8'))
old = json.load(open(KZ + '/kz_cards.json', encoding='utf-8'))
kzo = json.load(open('/home/claude/work/kanji_mn/kzo_v2.json', encoding='utf-8'))['order']
pos = {c: i for i, c in enumerate(kzo)}
want = json.load(open('/home/claude/scratch/k2b_list.json', encoding='utf-8'))
assert sorted(c['c'] for c in new) == sorted(want) and len(new) == 326
assert not ({c['c'] for c in new} & {c['c'] for c in old})
new.sort(key=lambda c: pos[c['c']])
D = json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8'))['kanji']
hira = lambda s: ''.join(chr(ord(ch) - 0x60) if 'ァ' <= ch <= 'ヶ' else ch for ch in s)
for c in new:   # 컴파일 때 앱 자료의 훈음·읽기가 들어감 — 지금 자료와 같은지
    k = D[c['c']]
    assert c['h'] == k['h'] and c['on'] == [hira(x) for x in k['on']] and c['kun'] == k['kun'], c['c']
allc = old + new
json.dump(allc, open(OUT + '/kz_cards_k2b.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
chk = json.load(open(OUT + '/kz_cards_k2b.json', encoding='utf-8'))
assert chk[:len(old)] == old and len(chk) == len(old) + 326
r = subprocess.run(['python3', KZ + '/kz_imp.py', OUT + '/kz_cards_k2b.json', OUT + '/kz_imp_k2b.json'], cwd=KZ, capture_output=True, text=True)
print(r.stdout.strip()[-1500:]); assert r.returncode == 0, r.stderr[-2000:]
oi = json.load(open(KZ + '/kz_imp.json', encoding='utf-8')); ni = json.load(open(OUT + '/kz_imp_k2b.json', encoding='utf-8'))
# 새 카드가 생기면 예문 속 여러 한자 덩어리(그 한자가 든 것)가 새로 나뉘어 옛 한자 점수도 조금 움직임(동점 근처 13자 순서가 뒤집힘 — 一 いつ↔ひと(つ) 같은 잡음)
# → 옛 1,108자 항목은 지금 것 그대로 두고(사용자가 본 빨간 읽기·대표 소리 그대로), 새 326자만 전체 계산 값으로 덧붙임(K2 기본 때와 같은 방식)
f = lambda x: (x['on'], x['kun'], x['rep'])
vis = [c for c in oi if f(oi[c]) != f(ni[c])]
print('옛 항목: 점수 달라진 것', sum(1 for c in oi if oi[c] != ni[c]), '· 앱에 보이는 것(순서·빨강·대표 소리)', len(vis), ''.join(vis), '→ 옛 값 그대로 씀')
out = dict(oi)
for c in new:
    assert c['c'] in ni, c['c']
    out[c['c']] = ni[c['c']]
json.dump(out, open(OUT + '/kz_imp_k2b.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('kz_cards', len(old), '+', len(new), '=', len(allc), '· kz_imp', len(out))
print('ok')
