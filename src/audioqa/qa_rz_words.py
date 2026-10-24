"""단어 음성 두 번째 받아쓰기(ReazonSpeech) 전수 — 한 줄씩 저장(이어하기)"""
import sys, json, os
from rz_check import rz_judge
W = json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8'))['words']
OUT = sys.argv[1]; done = set()
if os.path.exists(OUT):
    for l in open(OUT, encoding='utf-8'): done.add(json.loads(l)['key'])
fo = open(OUT, 'a', encoding='utf-8'); n = 0
for w in W:
    key = f"w/{w['id']}"
    if key in done: continue
    r = rz_judge(f"/home/claude/bjt-words/audio/w/{w['id']}.mp3", w['r'].replace('〜', ''))
    r.update(key=key, w=w['w'], r=w['r']); fo.write(json.dumps(r, ensure_ascii=False) + '\n'); fo.flush(); n += 1
    if n % 300 == 0: print(n, flush=True)
print('done', n)
