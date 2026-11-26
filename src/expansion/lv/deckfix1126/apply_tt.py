"""11/27 덱 예문 음성 고침 4개 — 앱 자료의 예문 음성 글(t)을 새 음성 글로(append_cards --tt와 같은 칸)"""
import json, sys
DP = sys.argv[1]
D = json.load(open(DP, encoding='utf-8')); W = {w['id']: w for w in D['words']}
for j in json.load(open('/home/claude/aqa/deckfix/jobs_final.json', encoding='utf-8')):
    i, n = map(int, j['f'].split('/')[-1][:-4].split('-'))
    print(i, n, W[i]['e'][n].get('t'), '→', j['t']); W[i]['e'][n]['t'] = j['t']
json.dump(D, open(DP, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
