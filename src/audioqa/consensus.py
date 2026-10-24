"""두 인식기 합의로 고르기: 후보마다 음소 받아쓰기(qa_ctx.judge) + 단어 받아쓰기(rz_check.rz_judge)
둘 다 정답이면 통과. 우선순위대로 첫 통과를 고름. 통과가 없으면 음소 통과 중 Δ(정답-ReazonSpeech가 들은 것)가 가장 큰 것.
usage: python3 consensus.py <jobs.json(fixgen 형식)> <outdir> [--keep-current <audio_dir>]
결과 <outdir>/cpick.json"""
import sys, os, json, asyncio, re
import numpy as np
from fixgen import syn, trim, safe, sem_new
from qa_ctx import judge, CAR, PE, QE
from rz_check import rz_judge
from phon import load16, logits, ctc_score
from kana import to_ph, norm
z = np.zeros(int(0.15 * 16000), np.float32)
def delta(fn, exp, alt, car):
    if not alt: return None
    PRE, POST = CAR[car]; lp = logits(np.concatenate([PRE, z, load16(fn), z, POST]))
    return round(ctc_score(lp, norm(PE + to_ph(exp) + QE)) - ctc_score(lp, norm(PE + to_ph(alt) + QE)), 2)
def evaluate(fn, exp, car):
    a = judge(fn, to_ph(exp), car=car); b = rz_judge(fn, exp, car)
    a.update(b); a['ph_ok'] = a['d'] == 0 and a['ctx_ok'] and not a['why']
    a['both'] = a['ph_ok'] and b['rz_ok']
    if a['ph_ok'] and not b['rz_ok']:
        alt = re.sub(r'[^ぁ-ゖ]', '', b['rz_kana'] or '')
        a['delta'] = delta(fn, exp, alt, car) if alt else None
    return a
async def gen(jobs, out):
    sem = sem_new(); tasks = []
    for j in jobs:
        for tag, v, t, rate in j['cands']:
            raw = f"{out}/{safe(j['name'])}.{tag}.raw.mp3"
            if not os.path.exists(raw): tasks.append(syn(sem, t, v, rate, raw))
    await asyncio.gather(*tasks)
if __name__ == '__main__':
    jobs = json.load(open(sys.argv[1], encoding='utf-8')); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    cur = sys.argv[sys.argv.index('--keep-current') + 1] if '--keep-current' in sys.argv else None
    asyncio.run(gen(jobs, out))
    pickp = f'{out}/cpick.json'; pick = json.load(open(pickp, encoding='utf-8')) if os.path.exists(pickp) else {}
    for j in jobs:
        tried = []
        if cur and os.path.exists(f"{cur}/{j['name']}.mp3"):
            fn = f"{cur}/{j['name']}.mp3"; car = j.get('cur_car', 'n')
            r = evaluate(fn, j['read'], car); r.update(tag='current', file=fn, v=None, t=None, rate=None); tried.append(r)
        if not (tried and tried[0]['both']):
            for tag, v, t, rate in j['cands']:
                raw = f"{out}/{safe(j['name'])}.{tag}.raw.mp3"; fn = raw.replace('.raw.mp3', '.mp3')
                if not os.path.exists(raw): continue
                if not os.path.exists(fn): trim(raw, fn, j['trim'])
                r = evaluate(fn, j['read'], 'k' if 'Keita' in v else 'n'); r.update(tag=tag, v=v, t=t, rate=rate, file=fn); tried.append(r)
                if r['both']: break
        best = next((r for r in tried if r['both']), None); how = 'both'
        if not best:
            ph = [r for r in tried if r['ph_ok'] and r.get('delta') is not None]
            best = max(ph, key=lambda r: r['delta']) if ph else None; how = 'best-delta'
        pick[j['name']] = dict(best, how=how, tried=[{k: r.get(k) for k in ('tag', 'got', 'rz_text', 'ph_ok', 'rz_ok', 'delta')} for r in tried]) if best else {'fail': True, 'tried': [{k: r.get(k) for k in ('tag', 'got', 'rz_text', 'ph_ok', 'rz_ok', 'delta')} for r in tried]}
        b = pick[j['name']]
        print(j['name'], j['read'], '->', 'FAIL' if b.get('fail') else f"{b['tag']} ({how}) ph:{b['got']} rz:{b['rz_text']} Δ:{b.get('delta')}", flush=True)
    json.dump(pick, open(pickp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
