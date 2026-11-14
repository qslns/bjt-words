"""11/14 K2: 새 그림 카드 한자의 소리 작업을 저장소 tools/kanji_voice_jobs.json에 덧붙임(옛 항목은 그대로).
usage: python3 k2_voice_add.py NEW_CARDS.json NEW_IMP.json
- 읽기 칩: 카드 on+kun 읽기마다 kr/<코드> — 없는 것만 {'key','t':'「읽기」'} 추가(10/21 규칙 그대로)
- 대표 소리: k/<한자 코드> = imp rep 읽기들의 kr 이어 붙이기. 게이타 목소리 kr이 섞이면 나머지는 krk/(게이타 판)로 맞춤
- 결과: 추가한 kr 키 목록을 /home/claude/aqa/k2/kr_new.json에 (받아쓰기용)"""
import sys, json, os
J_PATH = '/home/claude/bjt-words/tools/kanji_voice_jobs.json'
KEITA = 'ja-JP-KeitaNeural'
cards = json.load(open(sys.argv[1], encoding='utf-8')); imp = json.load(open(sys.argv[2], encoding='utf-8'))
J = json.load(open(J_PATH, encoding='utf-8'))
code = lambda s: '-'.join('%x' % ord(ch) for ch in s)
plain = lambda r: r.replace('(', '').replace(')', '').replace('（', '').replace('）', '')
KR = {x['key']: x for x in J['kr']}
added, rep_added = [], 0
def need(key, t, v=None):
    if key in KR: return
    e = {'key': key, 't': t}
    if v: e['v'] = v
    J['kr'].append(e); KR[key] = e; added.append(key)
for c in cards:
    ch = c['c']
    for r in c['on'] + c['kun']:
        r = plain(r); need('kr/' + code(r), '「' + r + '」')
    x = imp.get(ch)
    if not x: print('imp 없음', ch); continue
    k = 'k/' + code(ch)
    assert k not in J['rep'], ('이미 있는 대표 소리', ch)
    parts = ['kr/' + code(plain(r)) for r in x['rep']]
    if len(parts) > 1 and any(KR[p].get('v') == KEITA for p in parts):
        nxt = []
        for p, r in zip(parts, x['rep']):
            if KR[p].get('v') == KEITA: nxt.append(p)
            else:
                kk = 'krk/' + code(plain(r)); need(kk, '「' + plain(r) + '」', KEITA); nxt.append(kk)
        parts = nxt
    J['rep'][k] = parts; rep_added += 1
json.dump(J, open(J_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
os.makedirs('/home/claude/aqa/k2', exist_ok=True)
json.dump(added, open('/home/claude/aqa/k2/kr_new.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('kr 추가', len(added), '· 대표 소리 추가', rep_added, '· kr 전체', len(J['kr']), '· rep 전체', len(J['rep']))
