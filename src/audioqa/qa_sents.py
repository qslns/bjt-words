"""예문 음성 전수 받아쓰기 검사
usage: python3 qa_sents.py <data_app.json> <audio_dir> <out.json> [start] [end]"""
import sys, json, time
from phon import load16, logits, logits_chunked, greedy, ctc_score
from kana import norm, ed
from sent_exp import units_of
from align import heard_spans
D, A, OUT = sys.argv[1:4]
W = json.load(open(D, encoding='utf-8'))['words']
items = [(w['id'], i, e) for w in W for i, e in enumerate(w['e'])]
s0 = int(sys.argv[4]) if len(sys.argv) > 4 else 0; s1 = int(sys.argv[5]) if len(sys.argv) > 5 else len(items)
import os
done = set()
LP = os.environ.get('QA_JSONL', OUT + 'l')
if os.path.exists(LP):
    for line in open(LP, encoding='utf-8'):
        r = json.loads(line); done.add((r['id'], r['i']))
fo = open(LP, 'a', encoding='utf-8')   # 한 줄씩 바로 저장(중간에 멈춰도 이어서)
res = []; t0 = time.time()
for n, (wid, i, e) in enumerate(items[s0:s1]):
    if (wid, i) in done: continue
    U = units_of(e['j'])
    E = []; spans = []
    for kind, txt, ph in U: spans.append((len(E), len(E) + len(ph))); E += ph
    lp = logits_chunked(load16(f'{A}/s/{wid}-{i}.mp3')); G = greedy(lp)
    En, Gn = norm(E), norm(G)
    d, H = heard_spans(En, Gn, spans)
    base = ctc_score(lp, En)   # 정규화한 기대 음소(えい→ee, おう→oo, 무성 모음은 소문자)로 점수
    fl = []
    for (kind, txt, ph), (a, b), h in zip(U, spans, H):
        if not ph: continue
        ld = ed(En[a:b], h)
        if ld == 0: continue
        alt = En[:a] + list(h) + En[b:]
        mg = ctc_score(lp, alt) - base if alt else 0
        fl.append({'k': kind, 'u': txt, 'exp': ' '.join(ph), 'heard': ' '.join(h), 'ld': ld, 'mg': round(mg, 2)})
    r = {'id': wid, 'i': i, 'j': e['j'], 't': e.get('t', ''), 'd': d, 'n': len(En), 'got': ' '.join(G), 'fl': fl}
    res.append(r); fo.write(json.dumps(r, ensure_ascii=False) + '\n'); fo.flush()
    if n % 250 == 0: print(n, s1 - s0, round(time.time() - t0), flush=True)
fo.close()
allr = [json.loads(l) for l in open(LP, encoding='utf-8')]
json.dump(allr, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('done', len(allr), round(time.time() - t0))
