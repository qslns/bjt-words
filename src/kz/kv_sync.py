"""11/15: 한자 소리 작업 목록(tools/kanji_voice_jobs.json)을 카드·읽기 중요도에 맞춤 — k2_voice_add.py를 넓힌 것.
usage: python3 kv_sync.py CARDS.json IMP.json [--dry]
- 읽기 칩: 카드 on+kun 읽기마다 kr/<코드>(っ로 끝나는 읽기는 앱이 소리를 안 내서 뺌) — 없는 것만 {'key','t':'「읽기」'} 추가(10/21 규칙)
- 대표 소리: k/<한자 코드> = imp rep 읽기들의 kr 이어 붙이기. 게이타 목소리 kr이 섞이면 나머지는 krk/(게이타 판)로 맞춤.
  있던 항목도 rep가 바뀌었으면 고침(11/15: 읽기 중요도에 N3·N2 단어를 세면서 대표 소리가 바뀐 한자).
- 결과: 추가한 kr 키 → /home/claude/aqa/lf/kr_new.json(받아쓰기용), 바뀐 대표 소리 → /home/claude/aqa/lf/rep_changed.json"""
import sys, json, os
J_PATH = '/home/claude/bjt-words/tools/kanji_voice_jobs.json'
KEITA = 'ja-JP-KeitaNeural'
OUT = '/home/claude/aqa/lf'
cards = json.load(open(sys.argv[1], encoding='utf-8')); imp = json.load(open(sys.argv[2], encoding='utf-8'))
dry = '--dry' in sys.argv
J = json.load(open(J_PATH, encoding='utf-8'))
code = lambda s: '-'.join('%x' % ord(ch) for ch in s)
plain = lambda r: r.replace('(', '').replace(')', '').replace('（', '').replace('）', '')
KR = {x['key']: x for x in J['kr']}
added, changed, new_rep = [], [], []
def need(key, t, v=None):
    if key in KR: return
    e = {'key': key, 't': t}
    if v: e['v'] = v
    J['kr'].append(e); KR[key] = e; added.append(key)
for c in cards:
    ch = c['c']
    for r in c['on'] + c['kun']:
        r = plain(r)
        if r.endswith('っ'): continue
        need('kr/' + code(r), '「' + r + '」')
    x = imp.get(ch)
    if not x: print('imp 없음', ch); continue
    k = 'k/' + code(ch)
    parts = ['kr/' + code(plain(r)) for r in x['rep']]
    if len(parts) > 1 and any(KR[p].get('v') == KEITA for p in parts):
        nxt = []
        for p, r in zip(parts, x['rep']):
            if KR[p].get('v') == KEITA: nxt.append(p)
            else:
                kk = 'krk/' + code(plain(r)); need(kk, '「' + plain(r) + '」', KEITA); nxt.append(kk)
        parts = nxt
    old = J['rep'].get(k)
    if old == parts: continue
    if old is None: new_rep.append(k)
    else: changed.append([ch, old, parts])
    J['rep'][k] = parts
if not dry:
    json.dump(J, open(J_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    os.makedirs(OUT, exist_ok=True)
    json.dump(added, open(OUT + '/kr_new.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump(changed, open(OUT + '/rep_changed.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('kr 추가', len(added), added[:12], '· 대표 소리 새로', len(new_rep), '· 바뀜', len(changed), '· kr 전체', len(J['kr']), '· rep 전체', len(J['rep']), '(dry)' if dry else '')
