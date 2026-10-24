"""예문 다시 녹음: 후보 글(가나 바꿔 넣기 등)로 만들고, 예문 받아쓰기 검사(qa_sents와 같은 방식)로 통과한 것만 고름
usage: python3 sfix.py <jobs.json> <outdir>
jobs: [{name:'s/ID-I', cands:[[tag, voice, text, rate]], target:'구간 글자(확인용)'}]
판정: 후리가나 구간(seg)·숫자 들어간 구간에 들림이 다른 곳(mg>2)이 없고, 전체 음소 오류가 현재보다 늘지 않음"""
import sys, os, json, asyncio, re
from fixgen import syn, trim, safe, sem_new
from phon import load16, logits_chunked, greedy, ctc_score
from kana import norm, ed
from sent_exp import units_of
from align import heard_spans
from triage_s import benign
W = {w['id']: w for w in json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8'))['words']}
def qa_file(fn, j):
    U = units_of(j); E = []; spans = []
    for kind, txt, ph in U: spans.append((len(E), len(E) + len(ph))); E += ph
    lp = logits_chunked(load16(fn)); G = greedy(lp); En, Gn = norm(E), norm(G)
    d, H = heard_spans(En, Gn, spans); base = ctc_score(lp, En); bad = []
    for (kind, txt, ph), (a, b), h in zip(U, spans, H):
        if not ph or ed(En[a:b], h) == 0: continue
        mg = ctc_score(lp, En[:a] + list(h) + En[b:]) - base
        f = {'k': kind, 'u': txt, 'exp': ' '.join(ph), 'heard': ' '.join(h), 'mg': round(mg, 2)}
        if benign(f): continue
        dig = bool(re.search(r'[0-9０-９]', txt))
        if (kind == 'seg' and mg > 2) or (kind == 'txt' and (dig and mg > 0.5 or mg > 5)): bad.append(f)
    return {'d': d, 'n': len(En), 'got': ' '.join(G), 'bad': bad}
async def gen(jobs, out):
    sem = sem_new(); t = []
    for jb in jobs:
        for tag, v, text, rate in jb['cands']:
            raw = f"{out}/{safe(jb['name'])}.{tag}.raw.mp3"
            if not os.path.exists(raw): t.append(syn(sem, text, v, rate, raw))
    await asyncio.gather(*t)
if __name__ == '__main__':
    jobs = json.load(open(sys.argv[1], encoding='utf-8')); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    asyncio.run(gen(jobs, out))
    pickp = f'{out}/spick.json'; pick = json.load(open(pickp, encoding='utf-8')) if os.path.exists(pickp) else {}
    for jb in jobs:
        wid, i = map(int, jb['name'][2:].split('-')); j = W[wid]['e'][i]['j']
        cur = qa_file(f"/home/claude/bjt-words/audio/{jb['name']}.mp3", j)
        tried = [dict(cur, tag='current')]; best = None
        for tag, v, text, rate in jb['cands']:
            raw = f"{out}/{safe(jb['name'])}.{tag}.raw.mp3"; fn = raw.replace('.raw.mp3', '.mp3')
            if not os.path.exists(raw): continue
            if not os.path.exists(fn): trim(raw, fn, 'w')
            r = qa_file(fn, j); r.update(tag=tag, v=v, t=text, rate=rate, file=fn); tried.append(r)
            if not r['bad'] and r['d'] <= cur['d']:
                best = r; break
        pick[jb['name']] = dict(best, cur_bad=cur['bad'], tried=[{k: x.get(k) for k in ('tag', 'd', 'bad')} for x in tried]) if best else {'fail': True, 'tried': [{k: x.get(k) for k in ('tag', 'd', 'bad', 'got')} for x in tried]}
        b = pick[jb['name']]
        print(jb['name'], '->', 'FAIL' if b.get('fail') else f"{b['tag']} d {cur['d']}→{b['d']}", '|', jb.get('target', ''), flush=True)
    json.dump(pick, open(pickp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
